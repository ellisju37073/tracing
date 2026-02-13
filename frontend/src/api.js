const API_BASE = '/api'

// T18 Tideworks API
export async function scrapeT18(username, password) {
  const response = await fetch(`${API_BASE}/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Request failed')
  }

  return response.json()
}

export async function getSavedData() {
  const response = await fetch(`${API_BASE}/data`)
  
  if (!response.ok) {
    throw new Error('Failed to fetch saved data')
  }

  return response.json()
}

export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`)
  return response.json()
}

// ETSLink API
export async function getETSLinkLocations() {
  const response = await fetch(`${API_BASE}/etslink/locations`)
  if (!response.ok) {
    throw new Error('Failed to fetch locations')
  }
  return response.json()
}

export async function scrapeETSLink(username, password, locations) {
  const response = await fetch(`${API_BASE}/etslink/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password, locations }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Request failed')
  }

  return response.json()
}

export async function getETSLinkData() {
  const response = await fetch(`${API_BASE}/etslink/data`)
  if (!response.ok) {
    throw new Error('Failed to fetch ETSLink data')
  }
  return response.json()
}
