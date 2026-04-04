export const LOCATION_PRESETS = [
  {
    id: 'kathmandu',
    label: 'Kathmandu',
    description: 'Capital city baseline',
    latitude: 27.7172,
    longitude: 85.324,
    timezone: 'Asia/Kathmandu',
  },
  {
    id: 'pokhara',
    label: 'Pokhara',
    description: 'Western hill city',
    latitude: 28.2096,
    longitude: 83.9856,
    timezone: 'Asia/Kathmandu',
  },
  {
    id: 'biratnagar',
    label: 'Biratnagar',
    description: 'Eastern plains',
    latitude: 26.4525,
    longitude: 87.2718,
    timezone: 'Asia/Kathmandu',
  },
  {
    id: 'nepalgunj',
    label: 'Nepalgunj',
    description: 'Mid-western gateway',
    latitude: 28.0525,
    longitude: 81.6167,
    timezone: 'Asia/Kathmandu',
  },
];

export function findPresetByLocation(location = {}) {
  const latitude = Number(location.latitude);
  const longitude = Number(location.longitude);

  return LOCATION_PRESETS.find((preset) => (
    Math.abs(preset.latitude - latitude) < 0.01
    && Math.abs(preset.longitude - longitude) < 0.01
  )) || null;
}
