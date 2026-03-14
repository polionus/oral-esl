import { useState, useRef, useCallback } from 'react'
import './App.css'

function useTTS(engine) {
  const audioRef = useRef(null)

  const speak = useCallback((text) => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
    const url = `/api/tts?text=${encodeURIComponent(text)}&engine=${engine}`
    const audio = new Audio(url)
    audioRef.current = audio
    audio.play().catch(() => {})
  }, [engine])

  return speak
}

const categories = [
  {
    id: 'doctor',
    label: 'daktor',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/doctor-icon.png)', maskImage: 'url(/doctor-icon.png)' }} />
    ),
  },
  {
    id: 'navigation',
    label: 'duadui',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="3 11 22 2 13 21 11 13 3 11" />
      </svg>
    ),
  },
  {
    id: 'groceries',
    label: 'fottídin or hána',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="9" cy="21" r="1" />
        <circle cx="20" cy="21" r="1" />
        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
      </svg>
    ),
  },
  {
    id: 'restaurant',
    label: 'hóthel ',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 8h1a4 4 0 0 1 0 8h-1" />
        <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z" />
        <line x1="6" y1="1" x2="6" y2="4" />
        <line x1="10" y1="1" x2="10" y2="4" />
        <line x1="14" y1="1" x2="14" y2="4" />
      </svg>
    ),
  },
  {
    id: 'camera',
    label: 'sóbi',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
        <circle cx="12" cy="13" r="4" />
      </svg>
    ),
  },
]

const doctorOptions = [
  {
    id: 'doctor-pain',
    label: 'bic goré',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/headache.png)', maskImage: 'url(/headache.png)' }} />
    ),
  },
  {
    id: 'doctor-visit',
    label: 'boiyan gor',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/doctor-consultation.png)', maskImage: 'url(/doctor-consultation.png)' }} />
    ),
  },
]

const navigationOptions = [
  {
    id: 'nav-signboard',
    label: 'sáinbudh',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/signboard.png)', maskImage: 'url(/signboard.png)' }} />
    ),
  },
  {
    id: 'nav-ask-directions',
    label: 'mikká',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/hand-signal.png)', maskImage: 'url(/hand-signal.png)' }} />
    ),
  },
]

const groceryOptions = [
  {
    id: 'grocery-items',
    label: 'sáman',
    icon: (
      <img src="/vegetable.png" alt="Grocery Items" />
    ),
  },
  {
    id: 'grocery-conversation',
    label: 'hotáhoó',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/talking.png)', maskImage: 'url(/talking.png)' }} />
    ),
  },
]

const restaurantOptions = [
  {
    id: 'restaurant-food',
    label: 'hána',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/restaurant.png)', maskImage: 'url(/restaurant.png)' }} />
    ),
  },
  {
    id: 'restaurant-waiter',
    label: 'hotáhoó',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/talking.png)', maskImage: 'url(/talking.png)' }} />
    ),
  },
]

const groceryFlashcards = [
  { id: 'meat', emoji: '🥩', english: 'Meat', translation: 'Gusśó', pronunciation: 'Goos-sho' },
  { id: 'halal', emoji: '🍖', english: 'Halal', translation: 'Halal', pronunciation: 'Same as English/Arabic' },
  { id: 'rice-cooked', emoji: '🍚', english: 'Rice (cooked)', translation: 'Bat', pronunciation: 'Baht' },
  { id: 'rice-uncooked', emoji: '🌾', english: 'Rice (uncooked)', translation: 'Saul', pronunciation: 'Sha-ool' },
  { id: 'noodles', emoji: '🍝', english: 'Spaghetti/Noodles', translation: 'Núdhul', pronunciation: 'Noo-dhul' },
  { id: 'orange', emoji: '🍊', english: 'Orange', translation: 'Komola', pronunciation: 'Ko-mo-la' },
  { id: 'fruit', emoji: '🍎', english: 'Fruit', translation: 'Gula', pronunciation: 'Goo-la' },
  { id: 'vegetable', emoji: '🥬', english: 'Vegetable', translation: 'Torkari / Hóñsa', pronunciation: 'Tor-ka-ree / Hon-sha' },
  { id: 'bread', emoji: '🍞', english: 'Bread', translation: 'Ruti / Fira', pronunciation: 'Roo-tee / Fee-ra' },
]

function FlashCard({ card, speak }) {
  const [flipped, setFlipped] = useState(false)

  return (
    <button
      className={`flashcard ${flipped ? 'flipped' : ''}`}
      onClick={() => {
        if (!flipped) {
          setFlipped(true)
          speak(card.english)
        } else {
          setFlipped(false)
        }
      }}
    >
      <div className="flashcard-inner">
        <div className="flashcard-front">
          <span className="flashcard-emoji">{card.emoji}</span>
        </div>
        <div className="flashcard-back">
          <span className="flashcard-english">{card.english}</span>
          <span className="flashcard-translation">{card.translation}</span>
          <span className="flashcard-pronunciation">{card.pronunciation}</span>
        </div>
      </div>
    </button>
  )
}

function TTSToggle({ useElevenLabs, onToggle }) {
  return (
    <div className="tts-toggle">
      <span className="tts-toggle-label">AI Voice</span>
      <button
        className={`toggle-switch ${useElevenLabs ? 'active' : ''}`}
        onClick={onToggle}
        aria-label="Toggle ElevenLabs AI voice"
      >
        <span className="toggle-knob" />
      </button>
    </div>
  )
}

function App() {
  const [screen, setScreen] = useState('home')
  const [useElevenLabs, setUseElevenLabs] = useState(false)
  const engine = useElevenLabs ? 'elevenlabs' : 'gtts'
  const speak = useTTS(engine)

  if (screen === 'doctor') {
    return (
      <div className="container">
        <TTSToggle useElevenLabs={useElevenLabs} onToggle={() => setUseElevenLabs(!useElevenLabs)} />
        <button className="back-btn" onClick={() => setScreen('home')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5" />
            <path d="M12 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <div className="title-icon">
          {categories.find(c => c.id === 'doctor').icon}
        </div>
        <span className="pointing-hand" role="img" aria-label="point down">👇</span>
        <div className="sub-grid">
          {doctorOptions.map((opt) => (
            <button key={opt.id} className="category-item" onClick={() => console.log(opt.id)} onMouseEnter={() => speak(opt.label)}>
              <div className="category-circle">
                {opt.icon}
              </div>
              <span className="category-label">{opt.label}</span>
            </button>
          ))}
        </div>
      </div>
    )
  }

  if (screen === 'navigation') {
    return (
      <div className="container">
        <TTSToggle useElevenLabs={useElevenLabs} onToggle={() => setUseElevenLabs(!useElevenLabs)} />
        <button className="back-btn" onClick={() => setScreen('home')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5" />
            <path d="M12 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <div className="title-icon">
          {categories.find(c => c.id === 'navigation').icon}
        </div>
        <span className="pointing-hand" role="img" aria-label="point down">👇</span>
        <div className="sub-grid">
          {navigationOptions.map((opt) => (
            <button key={opt.id} className="category-item" onClick={() => console.log(opt.id)} onMouseEnter={() => speak(opt.label)}>
              <div className="category-circle">
                {opt.icon}
              </div>
              <span className="category-label">{opt.label}</span>
            </button>
          ))}
        </div>
      </div>
    )
  }

  if (screen === 'restaurant') {
    return (
      <div className="container">
        <TTSToggle useElevenLabs={useElevenLabs} onToggle={() => setUseElevenLabs(!useElevenLabs)} />
        <button className="back-btn" onClick={() => setScreen('home')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5" />
            <path d="M12 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <div className="title-icon">
          {categories.find(c => c.id === 'restaurant').icon}
        </div>
        <span className="pointing-hand" role="img" aria-label="point down">👇</span>
        <div className="sub-grid">
          {restaurantOptions.map((opt) => (
            <button key={opt.id} className="category-item" onClick={() => console.log(opt.id)} onMouseEnter={() => speak(opt.label)}>
              <div className="category-circle">
                {opt.icon}
              </div>
              <span className="category-label">{opt.label}</span>
            </button>
          ))}
        </div>
      </div>
    )
  }

  if (screen === 'grocery-flashcards') {
    return (
      <div className="container">
        <TTSToggle useElevenLabs={useElevenLabs} onToggle={() => setUseElevenLabs(!useElevenLabs)} />
        <button className="back-btn" onClick={() => setScreen('groceries')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5" />
            <path d="M12 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <div className="title-icon">
          <img src="/vegetable.png" alt="Grocery Items" />
        </div>
        <div className="flashcard-grid">
          {groceryFlashcards.map((card) => (
            <FlashCard key={card.id} card={card} speak={speak} />
          ))}
        </div>
      </div>
    )
  }

  if (screen === 'groceries') {
    return (
      <div className="container">
        <TTSToggle useElevenLabs={useElevenLabs} onToggle={() => setUseElevenLabs(!useElevenLabs)} />
        <button className="back-btn" onClick={() => setScreen('home')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5" />
            <path d="M12 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <div className="title-icon">
          {categories.find(c => c.id === 'groceries').icon}
        </div>
        <span className="pointing-hand" role="img" aria-label="point down">👇</span>
        <div className="sub-grid">
          {groceryOptions.map((opt) => (
            <button key={opt.id} className="category-item" onClick={() => opt.id === 'grocery-items' ? setScreen('grocery-flashcards') : console.log(opt.id)} onMouseEnter={() => speak(opt.label)}>
              <div className="category-circle">
                {opt.icon}
              </div>
              <span className="category-label">{opt.label}</span>
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <TTSToggle useElevenLabs={useElevenLabs} onToggle={() => setUseElevenLabs(!useElevenLabs)} />
      <h1>Oral ESL</h1>
      <span className="pointing-hand" role="img" aria-label="point down">👇</span>
      <div className="category-grid">
        {categories.map((cat) => (
          <button
            key={cat.id}
            className="category-item"
            onMouseEnter={() => speak(cat.label)}
            onClick={() => {
              if (cat.id === 'groceries') setScreen('groceries')
              else if (cat.id === 'doctor') setScreen('doctor')
              else if (cat.id === 'restaurant') setScreen('restaurant')
              else if (cat.id === 'navigation') setScreen('navigation')
              else console.log(cat.id)
            }}
          >
            <div className="category-circle">
              {cat.icon}
            </div>
            <span className="category-label">{cat.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default App
