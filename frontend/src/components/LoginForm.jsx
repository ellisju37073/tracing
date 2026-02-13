import { useState, useEffect } from 'react'
import { getETSLinkLocations } from '../api'

const ETSLINK_DEFAULT_LOCATIONS = [
  { code: 'LAX', name: 'Los Angeles' },
  { code: 'OAK', name: 'Oakland' },
  { code: 'TIW', name: 'Tacoma' },
]

function LoginForm({ onSubmit, isLoading, site }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [locations, setLocations] = useState(ETSLINK_DEFAULT_LOCATIONS)
  const [selectedLocations, setSelectedLocations] = useState([])

  useEffect(() => {
    if (site === 'etslink') {
      // Fetch locations from API
      getETSLinkLocations()
        .then(data => {
          if (data.locations) {
            setLocations(data.locations)
            setSelectedLocations(data.locations.map(l => l.code))
          }
        })
        .catch(() => {
          // Use defaults
          setSelectedLocations(ETSLINK_DEFAULT_LOCATIONS.map(l => l.code))
        })
    }
  }, [site])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (username && password) {
      const options = site === 'etslink' ? { locations: selectedLocations } : {}
      onSubmit(username, password, options)
    }
  }

  const toggleLocation = (code) => {
    setSelectedLocations(prev => 
      prev.includes(code)
        ? prev.filter(c => c !== code)
        : [...prev, code]
    )
  }

  const selectAllLocations = () => {
    setSelectedLocations(locations.map(l => l.code))
  }

  const clearLocations = () => {
    setSelectedLocations([])
  }

  return (
    <div style={styles.card}>
      <h2 style={styles.heading}>
        {site === 't18' ? '🚢 T18 Tideworks' : '📦 ETSLink'} Login
      </h2>
      <form onSubmit={handleSubmit}>
        <div style={styles.formGroup}>
          <label style={styles.label}>
            {site === 'etslink' ? 'User ID' : 'Username'}
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder={site === 'etslink' ? 'Enter your User ID' : 'Enter your username'}
            style={styles.input}
            disabled={isLoading}
            required
          />
        </div>
        <div style={styles.formGroup}>
          <label style={styles.label}>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            style={styles.input}
            disabled={isLoading}
            required
          />
        </div>

        {site === 'etslink' && (
          <div style={styles.formGroup}>
            <div style={styles.locationsHeader}>
              <label style={styles.label}>Locations ({selectedLocations.length})</label>
              <div style={styles.locationsActions}>
                <button type="button" onClick={selectAllLocations} style={styles.linkBtn}>
                  All
                </button>
                <button type="button" onClick={clearLocations} style={styles.linkBtn}>
                  None
                </button>
              </div>
            </div>
            <div style={styles.locationGrid}>
              {locations.map(loc => (
                <label key={loc.code} style={styles.locationItem}>
                  <input
                    type="checkbox"
                    checked={selectedLocations.includes(loc.code)}
                    onChange={() => toggleLocation(loc.code)}
                    disabled={isLoading}
                    style={styles.checkbox}
                  />
                  <span style={styles.locationCode}>{loc.code}</span>
                  <span style={styles.locationName}>{loc.name}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        <button 
          type="submit" 
          style={styles.button} 
          disabled={isLoading || (site === 'etslink' && selectedLocations.length === 0)}
        >
          {isLoading ? (
            <>
              <span style={styles.spinner}></span>
              Scraping...
            </>
          ) : (
            '🔍 Scrape Site'
          )}
        </button>
      </form>
    </div>
  )
}

const styles = {
  card: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '12px',
    padding: '1.5rem',
    border: '1px solid rgba(255, 255, 255, 0.1)',
  },
  heading: {
    fontSize: '1.1rem',
    marginBottom: '1rem',
    color: '#58a6ff',
  },
  formGroup: {
    marginBottom: '1rem',
  },
  label: {
    display: 'block',
    marginBottom: '0.5rem',
    color: '#ccc',
    fontSize: '0.9rem',
  },
  input: {
    width: '100%',
    padding: '0.75rem 1rem',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '8px',
    background: 'rgba(255, 255, 255, 0.05)',
    color: '#fff',
    fontSize: '1rem',
    outline: 'none',
  },
  button: {
    width: '100%',
    padding: '0.875rem',
    background: 'linear-gradient(135deg, #4f8cff 0%, #3b6fd4 100%)',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
  },
  spinner: {
    width: '16px',
    height: '16px',
    border: '2px solid rgba(255, 255, 255, 0.3)',
    borderRadius: '50%',
    borderTopColor: '#fff',
    animation: 'spin 1s linear infinite',
  },
  locationsHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.5rem',
  },
  locationsActions: {
    display: 'flex',
    gap: '0.75rem',
  },
  linkBtn: {
    background: 'none',
    border: 'none',
    color: '#58a6ff',
    cursor: 'pointer',
    fontSize: '0.85rem',
    padding: 0,
  },
  locationGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
    maxHeight: '200px',
    overflowY: 'auto',
    background: 'rgba(0, 0, 0, 0.2)',
    borderRadius: '8px',
    padding: '0.75rem',
  },
  locationItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    cursor: 'pointer',
    padding: '0.25rem 0',
  },
  checkbox: {
    width: '16px',
    height: '16px',
  },
  locationCode: {
    fontWeight: '600',
    color: '#58a6ff',
    minWidth: '40px',
  },
  locationName: {
    color: '#aaa',
    fontSize: '0.9rem',
  },
}

export default LoginForm
