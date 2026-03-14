import { useState } from 'react'
import './App.css'

const categories = [
  {
    id: 'doctor',
    label: 'Doctor Appointment',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/doctor-icon.png)', maskImage: 'url(/doctor-icon.png)' }} />
    ),
  },
  {
    id: 'navigation',
    label: 'Navigation',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="3 11 22 2 13 21 11 13 3 11" />
      </svg>
    ),
  },
  {
    id: 'groceries',
    label: 'Groceries',
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
    label: 'Restaurant',
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
    label: 'Take Image',
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
    label: 'Pain',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/headache.png)', maskImage: 'url(/headache.png)' }} />
    ),
  },
  {
    id: 'doctor-visit',
    label: 'Describe Pain',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/doctor-consultation.png)', maskImage: 'url(/doctor-consultation.png)' }} />
    ),
  },
]

const navigationOptions = [
  {
    id: 'nav-signboard',
    label: 'Signboard',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/signboard.png)', maskImage: 'url(/signboard.png)' }} />
    ),
  },
  {
    id: 'nav-ask-directions',
    label: 'Ask Directions',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/hand-signal.png)', maskImage: 'url(/hand-signal.png)' }} />
    ),
  },
]

const groceryOptions = [
  {
    id: 'grocery-items',
    label: 'Grocery Items',
    icon: (
      <img src="/vegetable.png" alt="Grocery Items" />
    ),
  },
  {
    id: 'grocery-conversation',
    label: 'Conversation',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/talking.png)', maskImage: 'url(/talking.png)' }} />
    ),
  },
]

const restaurantOptions = [
  {
    id: 'restaurant-food',
    label: 'Foods',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/restaurant.png)', maskImage: 'url(/restaurant.png)' }} />
    ),
  },
  {
    id: 'restaurant-waiter',
    label: 'Talk to Waiter',
    icon: (
      <span className="icon-mask" style={{ WebkitMaskImage: 'url(/talking.png)', maskImage: 'url(/talking.png)' }} />
    ),
  },
]

function App() {
  const [screen, setScreen] = useState('home')

  if (screen === 'doctor') {
    return (
      <div className="container">
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
            <button key={opt.id} className="category-item" onClick={() => console.log(opt.id)}>
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
            <button key={opt.id} className="category-item" onClick={() => console.log(opt.id)}>
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
            <button key={opt.id} className="category-item" onClick={() => console.log(opt.id)}>
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

  if (screen === 'groceries') {
    return (
      <div className="container">
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
            <button key={opt.id} className="category-item" onClick={() => console.log(opt.id)}>
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
      <h1>Oral ESL</h1>
      <span className="pointing-hand" role="img" aria-label="point down">👇</span>
      <div className="category-grid">
        {categories.map((cat) => (
          <button
            key={cat.id}
            className="category-item"
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
