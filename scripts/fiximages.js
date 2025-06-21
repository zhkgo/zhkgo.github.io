// scripts/image-path-fix.js
hexo.extend.filter.register('before_post_render', function (data) {
  data.content = data.content.replace(/\!\[(.*?)\]\((?!http)(images\/[^\)]+)\)/g, '![$1](/$2)');
  return data;
});
