// Kakao Maps API 타입 단언을 위해 window 확장
declare global {
  interface Window {
    kakao: any;
  }
}

export function tmapCoordsToKakao(coords: [number, number]): any {
  if (typeof window === "undefined" || !window.kakao) {
      // 서버사이드 빌드 방지 또는 SDK 미로드 시 대비
      return null;
  }
  const [lng, lat] = coords;
  return new window.kakao.maps.LatLng(lat, lng);
}
