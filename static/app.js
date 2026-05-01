const state = {
  assets: [],
  mode: null,
};

const elements = {
  assetGrid: document.querySelector("#assetGrid"),
  summary: document.querySelector("#summary"),
  modalBackdrop: document.querySelector("#modalBackdrop"),
  modalTitle: document.querySelector("#modalTitle"),
  form: document.querySelector("#assetForm"),
  formError: document.querySelector("#formError"),
  submitBtn: document.querySelector("#submitBtn"),
  toast: document.querySelector("#toast"),
};

const fields = {
  asset_id: document.querySelector("[data-field='asset_id']"),
  name: document.querySelector("[data-field='name']"),
  image_url: document.querySelector("[data-field='image_url']"),
  total: document.querySelector("[data-field='total']"),
  employee_id: document.querySelector("[data-field='employee_id']"),
};

const inputs = {
  asset_id: document.querySelector("#assetIdInput"),
  name: document.querySelector("#assetNameInput"),
  image_url: document.querySelector("#assetImageInput"),
  total: document.querySelector("#assetTotalInput"),
  employee_id: document.querySelector("#employeeIdInput"),
};

document.querySelector("#refreshBtn").addEventListener("click", loadAssets);
document.querySelector("#addAssetBtn").addEventListener("click", () => openModal("add"));
document.querySelector("#borrowBtn").addEventListener("click", () => openModal("borrow"));
document.querySelector("#returnBtn").addEventListener("click", () => openModal("return"));
document.querySelector("#closeModalBtn").addEventListener("click", closeModal);
document.querySelector("#cancelBtn").addEventListener("click", closeModal);
elements.modalBackdrop.addEventListener("click", (event) => {
  if (event.target === elements.modalBackdrop) {
    closeModal();
  }
});
elements.form.addEventListener("submit", handleSubmit);

loadAssets();

async function loadAssets() {
  try {
    const assets = await requestJson("/api/assets");
    state.assets = assets;
    renderSummary(assets);
    renderAssets(assets);
  } catch (error) {
    showToast(error.message || "资产列表加载失败");
  }
}

function renderSummary(assets) {
  const totalTypes = assets.length;
  const totalCount = assets.reduce((sum, asset) => sum + asset.total, 0);
  const remainingCount = assets.reduce((sum, asset) => sum + asset.remaining, 0);
  elements.summary.innerHTML = `
    <article class="summary-item">
      <strong>${totalTypes}</strong>
      <span>资产种类</span>
    </article>
    <article class="summary-item">
      <strong>${totalCount}</strong>
      <span>资产总量</span>
    </article>
    <article class="summary-item">
      <strong>${remainingCount}</strong>
      <span>可借数量</span>
    </article>
  `;
}

function renderAssets(assets) {
  if (!assets.length) {
    elements.assetGrid.innerHTML = "<p>暂无资产</p>";
    return;
  }

  elements.assetGrid.innerHTML = assets
    .map((asset) => {
      const percent = Math.round((asset.remaining / asset.total) * 100);
      const borrowers = asset.borrowers.length
        ? `<div class="borrowers">${asset.borrowers
            .map((employeeId) => `<span class="borrower">${escapeHtml(employeeId)}</span>`)
            .join("")}</div>`
        : `<p class="empty-borrowers">暂无借用人</p>`;

      return `
        <article class="asset-card">
          <img class="asset-image" src="${escapeAttribute(asset.image_url)}" alt="${escapeAttribute(asset.name)}" loading="lazy" />
          <div class="asset-body">
            <div class="asset-id">${escapeHtml(asset.asset_id)}</div>
            <div class="asset-name">${escapeHtml(asset.name)}</div>
            <div class="stock-line">
              <strong>剩余 ${asset.remaining}</strong>
              <span>总量 ${asset.total}</span>
            </div>
            <div class="progress" aria-label="剩余比例 ${percent}%">
              <div class="progress-bar" style="width: ${percent}%"></div>
            </div>
            ${borrowers}
          </div>
        </article>
      `;
    })
    .join("");
}

function openModal(mode) {
  state.mode = mode;
  elements.form.reset();
  setError("");

  const config = {
    add: {
      title: "添加资产",
      visibleFields: ["asset_id", "name", "image_url", "total"],
      submitText: "添加",
    },
    borrow: {
      title: "借用资产",
      visibleFields: ["asset_id", "employee_id"],
      submitText: "借用",
    },
    return: {
      title: "归还资产",
      visibleFields: ["asset_id", "employee_id"],
      submitText: "归还",
    },
  }[mode];

  elements.modalTitle.textContent = config.title;
  elements.submitBtn.textContent = config.submitText;

  Object.entries(fields).forEach(([name, field]) => {
    const visible = config.visibleFields.includes(name);
    field.classList.toggle("hidden", !visible);
    inputs[name].required = visible;
  });

  elements.modalBackdrop.classList.remove("hidden");
  inputs.asset_id.focus();
}

function closeModal() {
  elements.modalBackdrop.classList.add("hidden");
  state.mode = null;
}

async function handleSubmit(event) {
  event.preventDefault();
  setError("");
  elements.submitBtn.disabled = true;

  try {
    if (state.mode === "add") {
      await requestJson("/api/assets", {
        method: "POST",
        body: {
          asset_id: inputs.asset_id.value,
          name: inputs.name.value,
          image_url: inputs.image_url.value,
          total: Number(inputs.total.value),
        },
      });
      showToast("资产已添加");
    }

    if (state.mode === "borrow") {
      await requestJson(`/api/assets/${encodeURIComponent(inputs.asset_id.value)}/borrow`, {
        method: "POST",
        body: { employee_id: inputs.employee_id.value },
      });
      showToast("借用成功");
    }

    if (state.mode === "return") {
      await requestJson(`/api/assets/${encodeURIComponent(inputs.asset_id.value)}/return`, {
        method: "POST",
        body: { employee_id: inputs.employee_id.value },
      });
      showToast("归还成功");
    }

    closeModal();
    await loadAssets();
  } catch (error) {
    setError(error.message || "提交失败");
  } finally {
    elements.submitBtn.disabled = false;
  }
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Request-ID": crypto.randomUUID(),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const contentType = response.headers.get("Content-Type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const detail = payload?.detail;
    if (Array.isArray(detail)) {
      throw new Error(detail.map((item) => item.msg).join("；"));
    }
    throw new Error(detail || `请求失败：${response.status}`);
  }

  return payload;
}

function setError(message) {
  elements.formError.textContent = message;
  elements.formError.classList.toggle("hidden", !message);
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.remove("hidden");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    elements.toast.classList.add("hidden");
  }, 2400);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return entities[char];
  });
}

function escapeAttribute(value) {
  return escapeHtml(value);
}
