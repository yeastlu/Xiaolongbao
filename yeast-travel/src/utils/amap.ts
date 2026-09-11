export function amapSearchUrl(nameZh: string, cityZh: string) {
  const keyword = encodeURIComponent(`${nameZh} ${cityZh}`);
  return `https://uri.amap.com/search?keyword=${keyword}&src=yeast.travel&callnative=1`;
}

export function amapRouteUrl(stops: Array<{ nameZh: string }>, cityZh: string) {
  const query = stops.map((stop) => stop.nameZh).join(" → ");
  return amapSearchUrl(query, cityZh);
}
