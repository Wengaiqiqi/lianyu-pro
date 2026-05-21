export function createTransitPath(id) {
  const hashPath = `#/go/${id}`
  if (typeof window === 'undefined') return hashPath
  return `${window.location.origin}${window.location.pathname}${window.location.search}${hashPath}`
}

export function normalizeExternalUrl(url) {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  return `https://${url}`
}
