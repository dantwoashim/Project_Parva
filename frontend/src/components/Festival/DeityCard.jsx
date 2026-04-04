/**
 * DeityCard Component
 * ===================
 * 
 * Small card showing deity information.
 * Links to festivals featuring this deity.
 */

import PropTypes from 'prop-types';
import './DeityCard.css';

// Deity data - curated for major Hindu/Buddhist deities in Nepal
const DEITY_DATA = {
    'Shiva': {
        name: 'Lord Shiva',
        name_ne: 'भगवान शिव',
        emoji: '🔱',
        description: 'The Destroyer in the Hindu Trinity. Worshipped at Pashupatinath.',
        color: '#1E3A5F',
    },
    'Vishnu': {
        name: 'Lord Vishnu',
        name_ne: 'भगवान विष्णु',
        emoji: '🪷',
        description: 'The Preserver. Revered at Budhanilkantha and Changu Narayan.',
        color: '#4169E1',
    },
    'Krishna': {
        name: 'Lord Krishna',
        name_ne: 'भगवान कृष्ण',
        emoji: '🦚',
        description: 'Avatar of Vishnu. Worshipped at Krishna Mandir in Patan.',
        color: '#000080',
    },
    'Kali': {
        name: 'Goddess Kali',
        name_ne: 'देवी काली',
        emoji: '⚔️',
        description: 'Fierce goddess of time and destruction. Worshipped at Dakshinkali.',
        color: '#8B0000',
    },
    'Durga': {
        name: 'Goddess Durga',
        name_ne: 'देवी दुर्गा',
        emoji: '🦁',
        description: 'The invincible goddess. Central to Dashain celebrations.',
        color: '#DC143C',
    },
    'Kumari': {
        name: 'Living Goddess Kumari',
        name_ne: 'कुमारी देवी',
        emoji: '👧',
        description: 'Living incarnation of Taleju. Resides in Kumari Ghar.',
        color: '#C41E3A',
    },
    'Indra': {
        name: 'Lord Indra',
        name_ne: 'इन्द्र देव',
        emoji: '⚡',
        description: 'King of Gods and rain deity. Central to Indra Jatra.',
        color: '#FFD700',
    },
    'Bhairav': {
        name: 'Bhairav',
        name_ne: 'भैरव',
        emoji: '😈',
        description: 'Fierce manifestation of Shiva. Worshipped during Indra Jatra.',
        color: '#1E1E1E',
    },
    'Machhindranath': {
        name: 'Machhindranath',
        name_ne: 'मच्छिन्द्रनाथ',
        emoji: '🔴',
        description: 'God of rain and harvest. Central to Rato Machhindranath Jatra.',
        color: '#DC143C',
    },
    'Buddha': {
        name: 'Gautam Buddha',
        name_ne: 'गौतम बुद्ध',
        emoji: '☸️',
        description: 'The Enlightened One. Born in Lumbini, Nepal.',
        color: '#F4A460',
    },
    'Laxmi': {
        name: 'Goddess Laxmi',
        name_ne: 'देवी लक्ष्मी',
        emoji: '🪷',
        description: 'Goddess of wealth and prosperity. Central to Tihar.',
        color: '#FFD700',
    },
    'Ganesh': {
        name: 'Lord Ganesh',
        name_ne: 'भगवान गणेश',
        emoji: '🐘',
        description: 'Remover of obstacles. Invoked at beginnings of festivals.',
        color: '#FF6347',
    },
};

/**
 * DeityCard displays deity information in a compact card format.
 */
export function DeityCard({
    deityName,
    onClick,
    isActive = false,
    showDescription = true,
    size = 'medium',
}) {
    const deity = DEITY_DATA[deityName] || {
        name: deityName,
        name_ne: '',
        emoji: '🙏',
        description: 'A revered deity in Nepali tradition.',
        color: '#666666',
    };

    return (
        <div
            className={`deity-card deity-card--${size} ${isActive ? 'active' : ''}`}
            style={{ '--deity-color': deity.color }}
            onClick={() => onClick?.(deityName)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && onClick?.(deityName)}
        >
            <div className="deity-card__icon">
                <span className="deity-emoji">{deity.emoji}</span>
            </div>
            <div className="deity-card__info">
                <h4 className="deity-name">{deity.name}</h4>
                {deity.name_ne && (
                    <span className="deity-name-ne text-nepali">{deity.name_ne}</span>
                )}
                {showDescription && (
                    <p className="deity-description">{deity.description}</p>
                )}
            </div>
        </div>
    );
}

DeityCard.propTypes = {
    deityName: PropTypes.string.isRequired,
    onClick: PropTypes.func,
    isActive: PropTypes.bool,
    showDescription: PropTypes.bool,
    size: PropTypes.oneOf(['small', 'medium', 'large']),
};

export default DeityCard;
