import { useState } from 'react'

function DataViewer({ data, site }) {
  if (site === 'etslink' && data.locations) {
    return <ETSLinkDataViewer locations={data.locations} />
  }
  
  return <T18DataViewer data={data} />
}

function ETSLinkDataViewer({ locations }) {
  const [selectedLocation, setSelectedLocation] = useState(Object.keys(locations)[0])
  const locationData = locations[selectedLocation]

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>📦 ETSLink Data</h2>
        <div style={styles.stats}>
          <span style={styles.stat}>📍 {Object.keys(locations).length} locations</span>
        </div>
      </div>

      <div style={styles.locationTabs}>
        {Object.entries(locations).map(([code, loc]) => (
          <button
            key={code}
            style={{
              ...styles.locationTab,
              ...(selectedLocation === code ? styles.activeLocationTab : {}),
            }}
            onClick={() => setSelectedLocation(code)}
          >
            {code}
            {loc.error ? ' ⚠️' : ''}
          </button>
        ))}
      </div>

      {locationData && (
        <div style={styles.content}>
          {locationData.error ? (
            <div style={styles.error}>{locationData.error}</div>
          ) : (
            <>
              <div style={styles.locationInfo}>
                <h3>{locationData.location}</h3>
                <span style={styles.stat}>
                  {locationData.tables?.length || 0} tables, {locationData.links?.length || 0} links
                </span>
              </div>
              
              {locationData.tables && locationData.tables.length > 0 && (
                <TablesView tables={locationData.tables} />
              )}
              
              {locationData.links && locationData.links.length > 0 && (
                <div style={{ marginTop: '1.5rem' }}>
                  <h4 style={styles.sectionTitle}>Links</h4>
                  <LinksView links={locationData.links} />
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

function T18DataViewer({ data }) {
  const [activeTab, setActiveTab] = useState('links')

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>{data.title || 'Scraped Data'}</h2>
        <div style={styles.stats}>
          <span style={styles.stat}>🔗 {data.links?.length || 0} links</span>
          <span style={styles.stat}>📊 {data.tables?.length || 0} tables</span>
        </div>
      </div>

      <div style={styles.tabs}>
        <button
          style={{ ...styles.tab, ...(activeTab === 'links' ? styles.activeTab : {}) }}
          onClick={() => setActiveTab('links')}
        >
          Links
        </button>
        <button
          style={{ ...styles.tab, ...(activeTab === 'tables' ? styles.activeTab : {}) }}
          onClick={() => setActiveTab('tables')}
        >
          Tables
        </button>
      </div>

      <div style={styles.content}>
        {activeTab === 'links' && <LinksView links={data.links} />}
        {activeTab === 'tables' && <TablesView tables={data.tables} />}
      </div>
    </div>
  )
}

function LinksView({ links }) {
  if (!links || links.length === 0) {
    return <p style={styles.empty}>No links found</p>
  }

  return (
    <div style={styles.linkList}>
      {links.map((link, index) => (
        <a
          key={index}
          href={link.href}
          target="_blank"
          rel="noopener noreferrer"
          style={styles.link}
        >
          <span style={styles.linkText}>{link.text || 'Untitled'}</span>
          <span style={styles.linkHref}>{link.href}</span>
        </a>
      ))}
    </div>
  )
}

function TablesView({ tables }) {
  const [selectedTable, setSelectedTable] = useState(0)

  if (!tables || tables.length === 0) {
    return <p style={styles.empty}>No tables found</p>
  }

  const table = tables[selectedTable]

  return (
    <div>
      <div style={styles.tableSelector}>
        {tables.map((t, index) => (
          <button
            key={index}
            style={{
              ...styles.tableSelectorBtn,
              ...(selectedTable === index ? styles.activeTableBtn : {}),
            }}
            onClick={() => setSelectedTable(index)}
          >
            Table {index + 1} ({t.rowCount} rows)
          </button>
        ))}
      </div>

      <div style={styles.tableContainer}>
        <table style={styles.table}>
          {table.headers && table.headers.length > 0 && (
            <thead>
              <tr>
                {table.headers.map((header, i) => (
                  <th key={i} style={styles.th}>{header}</th>
                ))}
              </tr>
            </thead>
          )}
          <tbody>
            {table.rows.slice(0, 50).map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex} style={styles.td}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {table.rows.length > 50 && (
          <p style={styles.truncated}>Showing 50 of {table.rows.length} rows</p>
        )}
      </div>
    </div>
  )
}

const styles = {
  container: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '12px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    overflow: 'hidden',
  },
  header: {
    padding: '1.5rem',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  },
  title: {
    fontSize: '1.25rem',
    marginBottom: '0.5rem',
  },
  stats: {
    display: 'flex',
    gap: '1rem',
  },
  stat: {
    color: '#888',
    fontSize: '0.9rem',
  },
  tabs: {
    display: 'flex',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  },
  tab: {
    padding: '1rem 1.5rem',
    background: 'none',
    border: 'none',
    color: '#888',
    cursor: 'pointer',
    fontSize: '0.95rem',
    borderBottom: '2px solid transparent',
  },
  activeTab: {
    color: '#58a6ff',
    borderBottomColor: '#58a6ff',
  },
  content: {
    padding: '1.5rem',
    maxHeight: '500px',
    overflowY: 'auto',
  },
  empty: {
    color: '#666',
    textAlign: 'center',
    padding: '2rem',
  },
  linkList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  link: {
    display: 'block',
    padding: '0.75rem 1rem',
    background: 'rgba(255, 255, 255, 0.03)',
    borderRadius: '6px',
    textDecoration: 'none',
    transition: 'background 0.2s',
  },
  linkText: {
    color: '#58a6ff',
    display: 'block',
    marginBottom: '0.25rem',
  },
  linkHref: {
    color: '#666',
    fontSize: '0.8rem',
    wordBreak: 'break-all',
  },
  tableSelector: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.5rem',
    marginBottom: '1rem',
  },
  tableSelectorBtn: {
    padding: '0.5rem 1rem',
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '6px',
    color: '#888',
    cursor: 'pointer',
    fontSize: '0.85rem',
  },
  activeTableBtn: {
    background: 'rgba(88, 166, 255, 0.2)',
    borderColor: '#58a6ff',
    color: '#58a6ff',
  },
  tableContainer: {
    overflowX: 'auto',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '0.85rem',
  },
  th: {
    padding: '0.75rem',
    textAlign: 'left',
    background: 'rgba(255, 255, 255, 0.05)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    whiteSpace: 'nowrap',
  },
  td: {
    padding: '0.75rem',
    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
  },
  truncated: {
    color: '#666',
    fontSize: '0.85rem',
    marginTop: '1rem',
    textAlign: 'center',
  },
  locationTabs: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.5rem',
    padding: '1rem 1.5rem',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  },
  locationTab: {
    padding: '0.5rem 1rem',
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '6px',
    color: '#888',
    cursor: 'pointer',
    fontSize: '0.9rem',
    fontWeight: '600',
  },
  activeLocationTab: {
    background: 'rgba(88, 166, 255, 0.2)',
    borderColor: '#58a6ff',
    color: '#58a6ff',
  },
  locationInfo: {
    marginBottom: '1rem',
    paddingBottom: '1rem',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  },
  sectionTitle: {
    fontSize: '1rem',
    color: '#58a6ff',
    marginBottom: '0.75rem',
  },
  error: {
    color: '#f85149',
    padding: '1rem',
    background: 'rgba(248, 81, 73, 0.1)',
    borderRadius: '8px',
  },
}

export default DataViewer
