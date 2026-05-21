export const searchGroups = {
  站内: [
    { name: '站内', url: '__internal__', placeholder: '输入关键词搜索' },
  ],
  常用: [
    { name: '百度', url: 'https://www.baidu.com/s?wd=%s', placeholder: '百度一下' },
    { name: 'Google', url: 'https://www.google.com/search?q=%s', placeholder: 'Google 搜索' },
    { name: '站内', url: '__internal__', placeholder: '站内搜索' },
    { name: '淘宝', url: 'https://s.taobao.com/search?q=%s', placeholder: '淘宝搜索' },
    { name: 'Bing', url: 'https://cn.bing.com/search?q=%s', placeholder: 'Bing 搜索' },
  ],
  搜索: [
    { name: '百度', url: 'https://www.baidu.com/s?wd=%s', placeholder: '百度一下' },
    { name: 'Google', url: 'https://www.google.com/search?q=%s', placeholder: 'Google 搜索' },
    { name: '360', url: 'https://www.so.com/s?q=%s', placeholder: '360 搜索' },
    { name: '搜狗', url: 'https://www.sogou.com/web?query=%s', placeholder: '搜狗搜索' },
    { name: 'Bing', url: 'https://cn.bing.com/search?q=%s', placeholder: 'Bing 搜索' },
    { name: '神马', url: 'https://yz.m.sm.cn/s?q=%s', placeholder: '神马搜索' },
  ],
  工具: [
    { name: '权重查询', url: 'https://seo.chinaz.com/%s', placeholder: '请输入网址(不带 https://)' },
    { name: '备案查询', url: 'https://beian.miit.gov.cn/#/Integrated/recordQuery', placeholder: '备案查询' },
    { name: 'SEO查询', url: 'https://seo.chinaz.com/%s', placeholder: '请输入网址(不带 https://)' },
    { name: 'Whois', url: 'https://whois.chinaz.com/%s', placeholder: '请输入域名' },
    { name: 'Ping检测', url: 'https://ping.chinaz.com/%s', placeholder: '请输入网址' },
  ],
  社区: [
    { name: '知乎', url: 'https://www.zhihu.com/search?type=content&q=%s', placeholder: '知乎搜索' },
    { name: '微信', url: 'https://weixin.sogou.com/weixin?type=2&query=%s', placeholder: '微信文章搜索' },
    { name: '微博', url: 'https://s.weibo.com/weibo/%s', placeholder: '微博搜索' },
    { name: '豆瓣', url: 'https://www.douban.com/search?q=%s', placeholder: '豆瓣搜索' },
    { name: 'B站', url: 'https://search.bilibili.com/all?keyword=%s', placeholder: 'B站搜索' },
  ],
  生活: [
    { name: '淘宝', url: 'https://s.taobao.com/search?q=%s', placeholder: '淘宝搜索' },
    { name: '京东', url: 'https://search.jd.com/Search?keyword=%s', placeholder: '京东搜索' },
    { name: '下厨房', url: 'https://www.xiachufang.com/search/?keyword=%s', placeholder: '搜菜谱' },
    { name: '12306', url: 'https://www.12306.cn/index/', placeholder: '12306 购票' },
    { name: '快递100', url: 'https://www.kuaidi100.com/', placeholder: '查快递' },
    { name: '去哪儿', url: 'https://www.qunar.com/', placeholder: '去哪儿旅行' },
  ],
}

export const searchTabList = ['站内', '常用', '搜索', '工具', '社区', '生活']
