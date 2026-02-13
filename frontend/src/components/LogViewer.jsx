function LogViewer({ logs }) {
  return (
    <div style={styles.card}>
      <h2 style={styles.heading}>📋 Logs</h2>
      <div style={styles.logs}>
        {logs.length === 0 ? (
          <p style={styles.placeholder}>Waiting to start...</p>
        ) : (
          logs.map((log, index) => (
            <div key={index} style={{ ...styles.log, ...styles[log.type] }}>
              {log.type === 'success' && '✓ '}
              {log.type === 'error' && '✗ '}
              {log.type === 'info' && '→ '}
              {log.message}
            </div>
          ))
        )}
      </div>
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
  logs: {
    background: '#0d1117',
    borderRadius: '8px',
    padding: '1rem',
    fontFamily: "'Monaco', 'Menlo', monospace",
    fontSize: '0.85rem',
    lineHeight: '1.6',
    maxHeight: '300px',
    overflowY: 'auto',
  },
  log: {
    marginBottom: '0.25rem',
  },
  success: {
    color: '#3fb950',
  },
  error: {
    color: '#f85149',
  },
  info: {
    color: '#58a6ff',
  },
  placeholder: {
    color: '#666',
    fontStyle: 'italic',
  },
}

export default LogViewer
