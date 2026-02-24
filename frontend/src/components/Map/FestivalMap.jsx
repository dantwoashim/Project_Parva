/**
 * FestivalMap Component
 * =====================
 * 
 * Interactive map showing festival locations and temples.
 * Uses Leaflet for map rendering.
 */

import { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './FestivalMap.css';

// Fix Leaflet default marker icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom festival marker icon
const createFestivalIcon = (color = '#ff6b35', isActive = false) => {
    const size = isActive ? 40 : 30;
    return L.divIcon({
        className: 'festival-marker',
        html: `
      <div class="marker-inner ${isActive ? 'active' : ''}" style="background: ${color};">
        <span class="marker-icon">🎭</span>
      </div>
      ${isActive ? '<div class="marker-pulse" style="border-color: ' + color + '"></div>' : ''}
    `,
        iconSize: [size, size],
        iconAnchor: [size / 2, size],
        popupAnchor: [0, -size],
    });
};

// Temple/stupa marker icon
const createTempleIcon = (type = 'temple') => {
    const emoji = type === 'stupa' ? '☸️' : '🛕';
    return L.divIcon({
        className: 'temple-marker',
        html: `
      <div class="marker-inner temple">
        <span class="marker-icon">${emoji}</span>
      </div>
    `,
        iconSize: [28, 28],
        iconAnchor: [14, 28],
        popupAnchor: [0, -28],
    });
};

/**
 * MapController handles map movements and effects.
 */
function MapController({ selectedLocation, center }) {
    const map = useMap();

    useEffect(() => {
        if (selectedLocation) {
            map.flyTo(
                [selectedLocation.coordinates.lat, selectedLocation.coordinates.lng],
                15,
                { duration: 1.5 }
            );
        }
    }, [selectedLocation, map]);

    useEffect(() => {
        if (center && !selectedLocation) {
            map.flyTo([center.lat, center.lng], center.zoom || 12, {
                duration: 1,
            });
        }
    }, [center, selectedLocation, map]);

    return null;
}

/**
 * FestivalMap renders an interactive map of Nepal with festival locations.
 * Now fetches temple data from the backend API.
 */
export function FestivalMap({
    temples = [],
    selectedFestival,
    onFestivalSelect,
    onLocationClick,
    focusQuery = null,
    className = '',
    isLoading = false,
}) {
    const mapRef = useRef(null);
    const [selectedLocation, setSelectedLocation] = useState(null);

    // Nepal center coordinates
    const defaultCenter = { lat: 27.7172, lng: 85.3240, zoom: 12 };

    // Find locations for selected festival
    const activeLocationIds = selectedFestival?.id
        ? temples.filter(t => t.festivals?.includes(selectedFestival.id)).map(t => t.id)
        : [];

    // If festival selected, fly to first matching location
    useEffect(() => {
        if (selectedFestival && temples.length > 0) {
            const matchingTemple = temples.find(t =>
                t.festivals?.includes(selectedFestival.id)
            );
            if (matchingTemple) {
                setSelectedLocation(matchingTemple);
            } else {
                setSelectedLocation(null);
            }
        } else {
            setSelectedLocation(null);
        }
    }, [selectedFestival?.id, temples]);

    // External focus: used by ritual timeline location clicks to move map context.
    useEffect(() => {
        if (!focusQuery || temples.length === 0) return;

        if (typeof focusQuery === 'object' && focusQuery.coordinates) {
            setSelectedLocation(focusQuery);
            return;
        }

        const query = String(focusQuery).trim().toLowerCase();
        if (!query) return;

        const match = temples.find((temple) =>
            [temple.name, temple.name_ne, temple.id, temple.significance]
                .filter(Boolean)
                .some((value) => value.toLowerCase().includes(query))
        );

        if (match) {
            setSelectedLocation(match);
        }
    }, [focusQuery, temples]);

    const handleMarkerClick = (temple) => {
        setSelectedLocation(temple);
        onLocationClick?.(temple);
    };

    const getMarkerIcon = (temple, isActive) => {
        const color = isActive && selectedFestival?.primary_color
            ? selectedFestival.primary_color
            : '#ff6b35';

        if (temple.type === 'temple' || temple.type === 'shrine') {
            return createTempleIcon('temple');
        } else if (temple.type === 'stupa') {
            return createTempleIcon('stupa');
        }
        return createFestivalIcon(color, isActive);
    };

    return (
        <div className={`festival-map ${className} ${isLoading ? 'loading' : ''}`}>
            <MapContainer
                ref={mapRef}
                center={[defaultCenter.lat, defaultCenter.lng]}
                zoom={defaultCenter.zoom}
                className="festival-map__container"
                scrollWheelZoom={true}
                zoomControl={true}
            >
                <TileLayer
                    attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <MapController
                    selectedLocation={selectedLocation}
                    center={defaultCenter}
                />

                {/* Temple Markers from API */}
                {temples.map(temple => {
                    const isActive = activeLocationIds.includes(temple.id);

                    return (
                        <Marker
                            key={temple.id}
                            position={[temple.coordinates.lat, temple.coordinates.lng]}
                            icon={getMarkerIcon(temple, isActive)}
                            eventHandlers={{
                                click: () => handleMarkerClick(temple),
                            }}
                        >
                            <Popup className="festival-popup">
                                <div className="popup-content">
                                    <h3>{temple.name}</h3>
                                    {temple.name_ne && (
                                        <p className="popup-nepali">{temple.name_ne}</p>
                                    )}
                                    {temple.deity && (
                                        <p className="popup-deity">
                                            <span className="popup-label">Deity:</span> {temple.deity}
                                        </p>
                                    )}
                                    {temple.significance && (
                                        <p className="popup-description">{temple.significance}</p>
                                    )}
                                    {temple.role && (
                                        <p className="popup-role">
                                            <span className="popup-label">Role:</span> {temple.role}
                                        </p>
                                    )}
                                    {temple.festivals?.length > 0 && (
                                        <div className="popup-festivals">
                                            <span className="popup-label">Festivals:</span>
                                            <div className="popup-badges">
                                                {temple.festivals.slice(0, 3).map(festId => (
                                                    <span key={festId} className="popup-badge">
                                                        {festId.replace(/-/g, ' ')}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </Popup>
                        </Marker>
                    );
                })}
            </MapContainer>

            {/* Loading overlay */}
            {isLoading && (
                <div className="festival-map__loading">
                    <div className="loading-spinner" />
                    <span>Loading temples...</span>
                </div>
            )}

            {/* Map Legend */}
            <div className="festival-map__legend glass-card">
                <div className="legend-item">
                    <span className="legend-icon">🎭</span>
                    <span>Heritage Site</span>
                </div>
                <div className="legend-item">
                    <span className="legend-icon">🛕</span>
                    <span>Temple</span>
                </div>
                <div className="legend-item">
                    <span className="legend-icon">☸️</span>
                    <span>Stupa</span>
                </div>
                {selectedFestival && (
                    <div className="legend-active">
                        <span className="active-dot" style={{
                            background: selectedFestival.primary_color || 'var(--color-primary)'
                        }} />
                        <span>{selectedFestival.name} locations</span>
                    </div>
                )}
                <div className="legend-count">
                    {temples.length} locations
                </div>
            </div>
        </div>
    );
}

FestivalMap.propTypes = {
    temples: PropTypes.array,
    selectedFestival: PropTypes.object,
    onFestivalSelect: PropTypes.func,
    onLocationClick: PropTypes.func,
    focusQuery: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
    className: PropTypes.string,
    isLoading: PropTypes.bool,
};

export default FestivalMap;
