<template>
  <router-view />
</template>

<style>
:root {
  color-scheme: light;
  --app-bg: #f4f7fb;
  --app-bg-soft: #f9fbfe;
  --app-bg-elevated: #ffffff;
  --app-bg-muted: #edf3fb;
  --app-text: #142033;
  --app-text-soft: #61748a;
  --app-text-muted: #8a9aab;
  --app-border: #dce5f0;
  --app-border-strong: #c5d2e0;
  --app-primary: #2f80ed;
  --app-primary-strong: #1f6ad0;
  --app-primary-soft: rgba(47, 128, 237, 0.12);
  --app-success: #2fa36b;
  --app-warning: #e59b2f;
  --app-danger: #d95c5c;
  --app-shadow-sm: 0 10px 24px rgba(15, 23, 42, 0.06);
  --app-shadow: 0 18px 44px rgba(15, 23, 42, 0.08);
  --app-shadow-lg: 0 28px 70px rgba(15, 23, 42, 0.12);
  --app-radius-sm: 14px;
  --app-radius: 22px;
  --app-radius-lg: 30px;
  --app-content-width: 1760px;
  --app-content-narrow: 1520px;
  --app-header-height: 76px;
  --app-header-blur: blur(22px);
  --app-transition: 0.24s ease;
  --header-bg: rgba(244, 247, 251, 0.8);
  --header-border: rgba(220, 229, 240, 0.84);
  --header-text: #213246;
  --admin-aside-bg: #0f1c2d;
  --admin-aside-surface: rgba(255, 255, 255, 0.04);
  --admin-aside-text: rgba(230, 237, 245, 0.72);
  --admin-aside-active: #78b5ff;
  --admin-main-bg: linear-gradient(180deg, #f4f7fb 0%, #eef3f9 100%);
  --el-color-primary: var(--app-primary);
  --el-border-radius-base: 14px;
  --el-border-radius-small: 12px;
  --el-border-radius-round: 999px;
  --el-border-radius-circle: 50%;
  --el-fill-color-blank: var(--app-bg-elevated);
}

:root[data-theme='dark'] {
  color-scheme: dark;
  --app-bg: #08111c;
  --app-bg-soft: #0d1726;
  --app-bg-elevated: #111e2f;
  --app-bg-muted: #162334;
  --app-text: #ecf3fb;
  --app-text-soft: #97abc1;
  --app-text-muted: #70859c;
  --app-border: #233447;
  --app-border-strong: #32465e;
  --app-primary: #72b6ff;
  --app-primary-strong: #9fd0ff;
  --app-primary-soft: rgba(114, 182, 255, 0.14);
  --app-success: #51c88a;
  --app-warning: #ffbe62;
  --app-danger: #ff8c8c;
  --app-shadow-sm: 0 14px 30px rgba(0, 0, 0, 0.22);
  --app-shadow: 0 24px 56px rgba(0, 0, 0, 0.28);
  --app-shadow-lg: 0 32px 82px rgba(0, 0, 0, 0.36);
  --header-bg: rgba(8, 17, 28, 0.82);
  --header-border: rgba(35, 52, 71, 0.88);
  --header-text: #e6edf5;
  --admin-aside-bg: #091321;
  --admin-aside-surface: rgba(255, 255, 255, 0.05);
  --admin-aside-text: rgba(231, 238, 247, 0.72);
  --admin-aside-active: #8ec9ff;
  --admin-main-bg: linear-gradient(180deg, #08111c 0%, #0d1726 100%);
  --el-bg-color: var(--app-bg-elevated);
  --el-bg-color-overlay: #101d2d;
  --el-fill-color-blank: var(--app-bg-elevated);
  --el-fill-color: #132233;
  --el-fill-color-light: rgba(255, 255, 255, 0.04);
  --el-fill-color-lighter: rgba(255, 255, 255, 0.06);
  --el-fill-color-extra-light: rgba(255, 255, 255, 0.08);
  --el-text-color-primary: var(--app-text);
  --el-text-color-regular: var(--app-text);
  --el-text-color-secondary: var(--app-text-soft);
  --el-text-color-placeholder: var(--app-text-muted);
  --el-border-color: var(--app-border);
  --el-border-color-light: var(--app-border);
  --el-border-color-lighter: rgba(255, 255, 255, 0.08);
  --el-border-color-extra-light: rgba(255, 255, 255, 0.06);
  --el-mask-color: rgba(3, 8, 16, 0.72);
  --el-table-border-color: var(--app-border);
  --el-table-header-bg-color: #132233;
  --el-table-tr-bg-color: #101d2d;
  --el-table-row-hover-bg-color: #17283c;
  --el-table-current-row-bg-color: #17283c;
  --el-color-primary-light-9: rgba(114, 182, 255, 0.14);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  min-height: 100%;
  font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

html {
  background: var(--app-bg);
}

body {
  background:
    radial-gradient(circle at top, rgba(47, 128, 237, 0.08), transparent 38%),
    linear-gradient(180deg, var(--app-bg-soft) 0%, var(--app-bg) 100%);
  color: var(--app-text);
  transition:
    background-color var(--app-transition),
    color var(--app-transition);
}

a,
button,
input,
textarea,
select,
div,
section,
aside,
main,
header {
  transition:
    background-color var(--app-transition),
    color var(--app-transition),
    border-color var(--app-transition),
    box-shadow var(--app-transition),
    transform var(--app-transition);
}

a {
  color: inherit;
}

button {
  font: inherit;
}

.page-shell {
  max-width: var(--app-content-width);
  margin: 0 auto;
  width: 100%;
}

.page-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 28px;
  padding: 28px 30px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-lg);
  background:
    linear-gradient(135deg, rgba(47, 128, 237, 0.12) 0%, rgba(255, 255, 255, 0.86) 56%, rgba(255, 255, 255, 0.96) 100%);
  box-shadow: var(--app-shadow);
}

.page-hero h1,
.page-hero h2 {
  font-size: 30px;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--app-text);
}

.page-hero p {
  margin-top: 10px;
  color: var(--app-text-soft);
  font-size: 14px;
  line-height: 1.7;
}

.page-card,
.page-surface {
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, var(--app-bg-elevated) 100%);
  box-shadow: var(--app-shadow-sm);
}

.el-card,
.el-dialog,
.el-drawer,
.el-popover.el-popper,
.el-dropdown-menu,
.el-menu,
.el-input__wrapper,
.el-select__wrapper,
.el-textarea__inner,
.el-pagination.is-background .btn-next,
.el-pagination.is-background .btn-prev,
.el-pagination.is-background .el-pager li,
.el-tag,
.el-alert,
.el-empty,
.el-table,
.el-table__inner-wrapper,
.el-table__body-wrapper,
.el-table__header-wrapper {
  border-radius: var(--app-radius-sm);
}

.el-button {
  border-radius: var(--app-radius-sm);
}

.el-table,
.el-table__inner-wrapper {
  overflow: hidden;
}

.el-input__wrapper,
.el-select__wrapper,
.el-textarea__inner,
.el-popover.el-popper,
.el-dropdown-menu {
  box-shadow: var(--app-shadow-sm);
}

:root[data-theme='dark'] .page-hero {
  background:
    radial-gradient(circle at top left, rgba(114, 182, 255, 0.2), transparent 36%),
    linear-gradient(135deg, rgba(17, 30, 47, 0.96) 0%, rgba(13, 23, 38, 0.96) 100%);
  border-color: var(--app-border);
}

:root[data-theme='dark'] .page-card,
:root[data-theme='dark'] .page-surface {
  background: linear-gradient(180deg, rgba(17, 30, 47, 0.98) 0%, rgba(13, 23, 38, 0.98) 100%);
}

:root[data-theme='dark'] .el-menu {
  --el-menu-bg-color: transparent;
  --el-menu-text-color: var(--app-text-soft);
  --el-menu-hover-bg-color: rgba(255, 255, 255, 0.04);
  --el-menu-active-color: var(--app-primary);
}

:root[data-theme='dark'] .el-menu--horizontal > .el-menu-item:not(.is-disabled):hover,
:root[data-theme='dark'] .el-menu--horizontal > .el-sub-menu .el-sub-menu__title:hover {
  background-color: rgba(255, 255, 255, 0.04);
}

:root[data-theme='dark'] .el-card,
:root[data-theme='dark'] .el-table,
:root[data-theme='dark'] .el-input__wrapper,
:root[data-theme='dark'] .el-select__wrapper,
:root[data-theme='dark'] .el-select-dropdown,
:root[data-theme='dark'] .el-select-dropdown__item,
:root[data-theme='dark'] .el-popper.is-light,
:root[data-theme='dark'] .el-popper.is-light > .el-popper__arrow:before,
:root[data-theme='dark'] .el-popover.el-popper,
:root[data-theme='dark'] .el-tree-select__popper,
:root[data-theme='dark'] .el-textarea__inner,
:root[data-theme='dark'] .el-pagination.is-background .btn-next,
:root[data-theme='dark'] .el-pagination.is-background .btn-prev,
:root[data-theme='dark'] .el-pagination.is-background .el-pager li,
:root[data-theme='dark'] .el-dialog,
:root[data-theme='dark'] .el-dropdown-menu,
:root[data-theme='dark'] .el-empty__description p,
:root[data-theme='dark'] .el-form-item__label,
:root[data-theme='dark'] .el-breadcrumb__inner,
:root[data-theme='dark'] .el-breadcrumb__inner a,
:root[data-theme='dark'] .el-statistic__content,
:root[data-theme='dark'] .el-statistic__head {
  background-color: var(--app-bg-elevated);
  color: var(--app-text);
  border-color: var(--app-border);
}

:root[data-theme='dark'] .el-table th.el-table__cell,
:root[data-theme='dark'] .el-table td.el-table__cell,
:root[data-theme='dark'] .el-table tr,
:root[data-theme='dark'] .el-table,
:root[data-theme='dark'] .el-table__body-wrapper,
:root[data-theme='dark'] .el-table__header-wrapper,
:root[data-theme='dark'] .el-table__fixed,
:root[data-theme='dark'] .el-table__fixed-right,
:root[data-theme='dark'] .el-table__fixed::before,
:root[data-theme='dark'] .el-table__fixed-right::before,
:root[data-theme='dark'] .el-table__expanded-cell,
:root[data-theme='dark'] .el-table__inner-wrapper::before {
  background-color: var(--app-bg-elevated);
  color: var(--app-text);
  border-color: var(--app-border);
}

:root[data-theme='dark'] .el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell,
:root[data-theme='dark'] .el-table__body tr.hover-row > td.el-table__cell,
:root[data-theme='dark'] .el-table__body tr.current-row > td.el-table__cell {
  background-color: #17283c;
}

:root[data-theme='dark'] .el-button:not(.el-button--primary):not(.is-link) {
  background: var(--app-bg-elevated);
  border-color: var(--app-border);
  color: var(--app-text);
}

:root[data-theme='dark'] .el-input-group__append,
:root[data-theme='dark'] .el-input-group__prepend {
  background: var(--app-bg-soft);
  border-color: var(--app-border);
  color: var(--app-text);
  box-shadow: none;
}

:root[data-theme='dark'] .el-select-dropdown__item.is-hovering,
:root[data-theme='dark'] .el-select-dropdown__item:hover,
:root[data-theme='dark'] .el-tree-node__content:hover {
  background: rgba(255, 255, 255, 0.06);
}

:root[data-theme='dark'] .el-select-dropdown__item.is-selected {
  color: #9fd0ff;
}

:root[data-theme='dark'] .el-input__inner,
:root[data-theme='dark'] .el-textarea__inner,
:root[data-theme='dark'] .el-select__selected-item,
:root[data-theme='dark'] .el-select__placeholder,
:root[data-theme='dark'] .el-pagination,
:root[data-theme='dark'] .el-empty__description p {
  color: var(--app-text);
}

:root[data-theme='dark'] .el-overlay {
  background-color: rgba(3, 8, 16, 0.72);
}

:root[data-theme='dark'] .el-tag {
  --el-tag-bg-color: rgba(114, 182, 255, 0.14);
  --el-tag-border-color: rgba(114, 182, 255, 0.22);
  --el-tag-text-color: #9fd0ff;
}

@media (max-width: 768px) {
  .page-hero {
    padding: 22px 18px;
    border-radius: var(--app-radius);
    flex-direction: column;
    align-items: flex-start;
  }

  .page-hero h1,
  .page-hero h2 {
    font-size: 24px;
  }
}

@media (min-width: 1280px) {
  .page-shell {
    padding-inline: 8px;
  }

  .page-hero {
    padding: 34px 38px;
    gap: 32px;
  }

  .page-hero h1,
  .page-hero h2 {
    font-size: 34px;
  }

  .page-card,
  .page-surface {
    border-radius: 24px;
  }

  .el-card {
    --el-card-padding: 24px;
  }

  .el-table {
    font-size: 14px;
  }

  .el-table th.el-table__cell,
  .el-table td.el-table__cell {
    padding-top: 14px;
    padding-bottom: 14px;
  }
}
</style>
