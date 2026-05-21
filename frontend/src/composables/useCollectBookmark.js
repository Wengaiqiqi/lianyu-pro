import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import { addBookmark } from '@/api/bookmark'
import { getToken } from '@/utils/auth'

function getBookmarkKey(item) {
  return item?.id ?? item?.url
}

export function useCollectBookmark() {
  const collectingKeys = ref([])

  function isCollecting(item) {
    return collectingKeys.value.includes(getBookmarkKey(item))
  }

  async function collectBookmark(item) {
    if (!getToken()) {
      ElMessage.warning('请先登录后再加入我的链域')
      return
    }

    if (!item?.url || !item?.title) {
      ElMessage.warning('该网站缺少必要信息，暂时无法加入')
      return
    }

    const key = getBookmarkKey(item)
    if (!key || collectingKeys.value.includes(key)) {
      return
    }

    collectingKeys.value = [...collectingKeys.value, key]

    try {
      await addBookmark({
        url: item.url,
        title: item.title,
        description: item.description || '',
        favicon: item.favicon || '',
        category_id: item.category_id || null,
        is_public: false,
      })
      ElMessage.success('已加入我的链域')
    } catch (error) {
      // 错误提示已在 request 拦截器中处理
    } finally {
      collectingKeys.value = collectingKeys.value.filter((current) => current !== key)
    }
  }

  return {
    collectBookmark,
    isCollecting,
  }
}
