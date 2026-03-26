/**
 * 두 좌표 사이의 거리 (미터)
 * @param {[number, number]} from - [lat, lng]
 * @param {[number, number]} to - [lat, lng]
 * @returns {number} distance in meters
 */
export const haversine = (from, to) => {
  const R = 6371000; // 지구 반지름 (미터)
  const [lat1, lng1] = from;
  const [lat2, lng2] = to;

  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

/**
 * 두 경로 점 사이의 중간점 생성 (100m 간격)
 */
export const fillGapsBetweenPoints = (coords, maxGapMeters = 100) => {
  const result = [];
  for (let i = 0; i < coords.length - 1; i++) {
    result.push(coords[i]);
    const dist = haversine(coords[i], coords[i + 1]);
    const steps = Math.ceil(dist / maxGapMeters);

    for (let j = 1; j < steps; j++) {
      const ratio = j / steps;
      const [lat1, lng1] = coords[i];
      const [lat2, lng2] = coords[i + 1];
      result.push([
        lat1 + (lat2 - lat1) * ratio,
        lng1 + (lng2 - lng1) * ratio,
      ]);
    }
  }
  result.push(coords[coords.length - 1]);
  return result;
};
