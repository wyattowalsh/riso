/**
 * Documentation Search Integration
 *
 * Searches the Sphinx-generated docs index for full-text results.
 * Fetches and parses /docs/searchindex.js at runtime.
 */

export interface DocSearchResult {
  title: string
  url: string
  docName: string
  score: number
  excerpt?: string
}

interface SphinxIndex {
  alltitles: Record<string, [number, string | null][]>
  docnames: string[]
  terms: Record<string, number | number[]>
  titles: string[]
}

let cachedIndex: SphinxIndex | null = null

/**
 * Load and parse the Sphinx search index
 */
export async function loadDocsIndex(): Promise<SphinxIndex | null> {
  if (cachedIndex) return cachedIndex

  try {
    const response = await fetch('/docs/searchindex.js')
    if (!response.ok) return null

    const text = await response.text()
    // Parse the Search.setIndex({...}) format
    const jsonMatch = text.match(/Search\.setIndex\((\{[\s\S]*\})\)/)
    if (!jsonMatch) return null

    cachedIndex = JSON.parse(jsonMatch[1])
    return cachedIndex
  } catch {
    return null
  }
}

/**
 * Search the documentation index
 */
export async function searchDocs(query: string): Promise<DocSearchResult[]> {
  const index = await loadDocsIndex()
  if (!index || query.length < 2) return []

  const results: DocSearchResult[] = []
  const queryLower = query.toLowerCase()
  const queryTerms = queryLower.split(/\s+/).filter(t => t.length > 1)

  // Search titles first (higher priority)
  for (const [title, refs] of Object.entries(index.alltitles)) {
    const titleLower = title.toLowerCase()
    let score = 0

    // Exact match in title
    if (titleLower === queryLower) {
      score = 100
    } else if (titleLower.includes(queryLower)) {
      score = 80
    } else {
      // Check if any query term matches
      for (const term of queryTerms) {
        if (titleLower.includes(term)) {
          score = Math.max(score, 50)
        }
      }
    }

    if (score > 0) {
      for (const [docId, anchor] of refs) {
        const docName = index.docnames[docId]
        const url = `/docs/${docName}.html${anchor ? '#' + anchor : ''}`
        results.push({
          title,
          url,
          docName,
          score,
        })
      }
    }
  }

  // Search terms index for deeper matches
  for (const term of queryTerms) {
    if (index.terms[term]) {
      const docIds = Array.isArray(index.terms[term])
        ? index.terms[term] as number[]
        : [index.terms[term] as number]

      for (const docId of docIds) {
        const docName = index.docnames[docId]
        // Check if we already have this doc
        const existing = results.find(r => r.docName === docName)
        if (!existing) {
          results.push({
            title: formatDocName(docName),
            url: `/docs/${docName}.html`,
            docName,
            score: 30,
          })
        }
      }
    }
  }

  // Sort by score and dedupe
  const seen = new Set<string>()
  return results
    .sort((a, b) => b.score - a.score)
    .filter(r => {
      if (seen.has(r.url)) return false
      seen.add(r.url)
      return true
    })
    .slice(0, 8)
}

/**
 * Format a document name into a readable title
 */
function formatDocName(docName: string): string {
  // Handle paths like "guides/quickstart" -> "Quickstart"
  const parts = docName.split('/')
  const name = parts[parts.length - 1]
  return name
    .replace(/-/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())
}
