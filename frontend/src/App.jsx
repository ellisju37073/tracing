import { useState } from 'react'
import LoginForm from './components/LoginForm'
import LogViewer from './components/LogViewer'
import DataViewer from './components/DataViewer'
import { scrapeT18, scrapeETSLink, getETSLinkLocations } from './api'

const SITES = {
  t18: { name: 'T18 Tideworks', icon: '🚢' },
  etslink: { name: 'ETSLink', icon: '📦' },
}

function App() {
  const [activeSite, setActiveSite] = useState('t18')
  const [isLoading, setIsLoading] = useState(false)
  const [logs, setLogs] = useState([])
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const handleScrape = async (username, password, options = {}) => {
    setIsLoading(true)
    setLogs([])
    setData(null)
    setError(null)

    try {
      let result
      if (activeSite === 't18') {
        result = await scrapeT18(username, password)
        setLogs(result.logs || [])
        if (result.success) {
          setData(result.data)
        } else {
          setError(result.error || 'Scraping failed')
        }
      } else if (activeSite === 'etslink') {
        result = await scrapeETSLink(username, password, options.locations)
        setLogs(result.logs || [])
        if (result.success) {
          setData({ locations: result.locations })
        } else {
          setError(result.error || 'Scraping failed')
        }
      }
    } catch (err) {
      setError(err.message)
      setLogs([{ type: 'error', message: err.message }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>🚢 Terminal Scraper</h1>
        <p style={styles.subtitle}>Scrape data from shipping terminal portals</p>
        
        <div style={styles.siteTabs}>
          {Object.entries(SITES).map(([key, site]) => (
            <button
              key={key}
              style={{
                ...styles.siteTab,
                ...(activeSite === key ? styles.activeSiteTab : {}),
              }}
              onClick={() => {
                setActiveSite(key)
                setData(null)
                setLogs([])
                setError(null)
              }}
            >
              {site.icon} {site.name}
            </button>
          ))}
        </div>
      </header>

      <main style={styles.main}>
        <div style={styles.sidebar}>
          <LoginForm 
            onSubmit={handleScrape} 
            isLoading={isLoading}
            site={activeSite}
          />
          <LogViewer logs={logs} />
        </div>

        <div style={styles.content}>
          {error && (
            <div style={styles.errorBanner}>
              ❌ {error}
            </div>
          )}
          {data && <DataViewer data={data} site={activeSite} />}
          {!data && !isLoading && (
            <div style={styles.placeholder}>
              <p>Enter your credentials and click "Scrape" to get started</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    padding: '2rem',
  },
  header: {
    textAlign: 'center',
    marginBottom: '2rem',
  },
  title: {
    fontSize: '2.5rem',
    marginBottom: '0.5rem',
  },
  subtitle: {
    color: '#888',
    marginBottom: '1.5rem',
  },
  siteTabs: {
    display: 'flex',
    justifyContent: 'center',
    gap: '0.5rem',
  },
  siteTab: {
    padding: '0.75rem 1.5rem',
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    color: '#888',
    cursor: 'pointer',
    fontSize: '0.95rem',
    transition: 'all 0.2s',
  },
  activeSiteTab: {
    background: 'rgba(88, 166, 255, 0.2)',
    borderColor: '#58a6ff',
    color: '#58a6ff',
  },
  main: {
    display: 'grid',
    gridTemplateColumns: '380px 1fr',
    gap: '2rem',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  sidebar: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  content: {
    minHeight: '500px',
  },
  errorBanner: {
    background: 'rgba(248, 81, 73, 0.2)',
    border: '1px solid #f85149',
    borderRadius: '8px',
    padding: '1rem',
    marginBottom: '1rem',
  },
  placeholder: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '300px',
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '12px',
    color: '#666',
  },
}

export default App
