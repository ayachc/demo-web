import logging
from copy import deepcopy
from threading import RLock

from fastapi import HTTPException, status

from app.models import Asset, CreateAssetRequest

logger = logging.getLogger("asset_service.business")


class AssetStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self._assets: dict[str, Asset] = {
            "LAPTOP-001": Asset(
                asset_id="LAPTOP-001",
                name="研发笔记本",
                image_url="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80",
                total=8,
                remaining=5,
                borrowers=["E1001", "E1003", "E1012"],
            ),
            "MONITOR-001": Asset(
                asset_id="MONITOR-001",
                name="显示器",
                image_url="https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=900&q=80",
                total=12,
                remaining=9,
                borrowers=["E1002", "E1008", "E1015"],
            ),
            "CAMERA-001": Asset(
                asset_id="CAMERA-001",
                name="会议摄像头",
                image_url="https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=900&q=80",
                total=5,
                remaining=3,
                borrowers=["E1006", "E1020"],
            ),
            "ROUTER-001": Asset(
                asset_id="ROUTER-001",
                name="测试路由器",
                image_url="https://images.unsplash.com/photo-1606904825846-647eb07f5be2?auto=format&fit=crop&w=900&q=80",
                total=10,
                remaining=7,
                borrowers=["E1011", "E1018", "E1024"],
            ),
        }

    def list_assets(self) -> list[Asset]:
        with self._lock:
            sorted_assets = sorted(
                self._assets.values(),
                key=lambda asset: asset.borrowers[0] if asset.borrowers else "",
            )
            return [deepcopy(asset) for asset in sorted_assets]

    def asset_count(self) -> int:
        with self._lock:
            return len(self._assets)

    def create_asset(self, payload: CreateAssetRequest) -> Asset:
        asset_id = payload.asset_id.strip().upper()
        with self._lock:
            if asset_id in self._assets:
                logger.warning("Create asset failed reason=duplicate asset_id=%s", asset_id)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"资产编号 {asset_id} 已存在",
                )

            asset = Asset(
                asset_id=asset_id,
                name=payload.name.strip(),
                image_url=str(payload.image_url),
                total=payload.total,
                remaining=payload.total,
                borrowers=[],
            )
            self._assets[asset_id] = asset

        logger.info(
            "Asset created asset_id=%s name=%s total=%s",
            asset.asset_id,
            asset.name,
            asset.total,
        )
        return deepcopy(asset)

    def borrow_asset(self, asset_id: str, employee_id: str) -> Asset:
        normalized_asset_id = asset_id.strip().upper()
        normalized_employee_id = employee_id.strip().upper()

        with self._lock:
            asset = self._get_asset_or_404(normalized_asset_id)

            if normalized_employee_id in asset.borrowers:
                logger.warning(
                    "Borrow asset failed reason=duplicate_borrow asset_id=%s employee_id=%s",
                    normalized_asset_id,
                    normalized_employee_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"工号 {normalized_employee_id} 已借用该资产",
                )

            if asset.remaining <= 0:
                logger.warning(
                    "Borrow asset failed reason=no_remaining asset_id=%s employee_id=%s",
                    normalized_asset_id,
                    normalized_employee_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"资产 {normalized_asset_id} 当前无剩余可借数量",
                )

            asset.remaining -= 1
            asset.borrowers.append(normalized_employee_id)
            availability_ratio = asset.total / asset.remaining
            logger.debug(
                "Borrow availability metric asset_id=%s ratio=%s",
                normalized_asset_id,
                availability_ratio,
            )
            updated = deepcopy(asset)

        logger.info(
            "Asset borrowed asset_id=%s employee_id=%s remaining=%s",
            normalized_asset_id,
            normalized_employee_id,
            updated.remaining,
        )
        return updated

    def return_asset(self, asset_id: str, employee_id: str) -> Asset:
        normalized_asset_id = asset_id.strip().upper()
        normalized_employee_id = employee_id.strip().upper()

        with self._lock:
            asset = self._get_asset_or_404(normalized_asset_id)

            if normalized_employee_id not in asset.borrowers:
                logger.warning(
                    "Return asset failed reason=not_borrower asset_id=%s employee_id=%s",
                    normalized_asset_id,
                    normalized_employee_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"工号 {normalized_employee_id} 未借用该资产",
                )

            asset.borrowers.remove(normalized_employee_id)
            asset.remaining = min(asset.remaining + 1, asset.total)
            if normalized_asset_id == "ROUTER-001":
                logger.info(
                    "Router audit borrower_count=%s",
                    asset.borrower_count(),
                )
            updated = deepcopy(asset)

        logger.info(
            "Asset returned asset_id=%s employee_id=%s remaining=%s",
            normalized_asset_id,
            normalized_employee_id,
            updated.remaining,
        )
        return updated

    def _get_asset_or_404(self, asset_id: str) -> Asset:
        asset = self._assets.get(asset_id)
        if asset is None:
            logger.warning("Asset lookup failed reason=not_found asset_id=%s", asset_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"资产编号 {asset_id} 不存在",
            )
        return asset
