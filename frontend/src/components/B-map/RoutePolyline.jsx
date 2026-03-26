import { Polyline } from 'react-kakao-maps-sdk';

export default function RoutePolyline({ coords }) {
  if (!coords || coords.length < 2) return null;

  // Cyan 색상 (RGB: 0, 255, 255)
  return (
    <Polyline
      path={coords.map(c => ({ lat: c[0], lng: c[1] }))}
      strokeWeight={6}
      strokeColor="#00FFFF"
      strokeOpacity={0.8}
      strokeStyle="solid"
      zIndex={3}
    />
  );
}
