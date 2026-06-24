// Confetti colors matching RISO ink palette
const CONFETTI_COLORS = [
  '#0078BF', // federal blue
  '#FF665E', // bright red
  '#FFE800', // sunflower
  '#00A95C', // green
  '#FF6C2F', // orange
  '#FF48B0', // fluorescent pink
  '#00838A', // teal
  '#765BA7', // grape
]

/**
 * Creates a confetti burst effect at the specified coordinates
 * @param x - X coordinate for the confetti origin
 * @param y - Y coordinate for the confetti origin
 */
export function createConfetti(x: number, y: number) {
  const container = document.createElement('div')
  container.className = 'confetti-container'
  document.body.appendChild(container)

  for (let i = 0; i < 30; i++) {
    const confetti = document.createElement('div')
    confetti.className = 'confetti'
    confetti.style.left = `${x}px`
    confetti.style.top = `${y}px`
    confetti.style.backgroundColor = CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)]
    confetti.style.transform = `rotate(${Math.random() * 360}deg)`
    confetti.style.width = `${8 + Math.random() * 8}px`
    confetti.style.height = `${8 + Math.random() * 8}px`
    confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px'

    // Random direction
    const angle = (Math.random() * 360 * Math.PI) / 180
    const velocity = 150 + Math.random() * 200
    const vx = Math.cos(angle) * velocity
    const vy = Math.sin(angle) * velocity

    confetti.animate([
      {
        transform: `translate(0, 0) rotate(0deg)`,
        opacity: 1,
      },
      {
        transform: `translate(${vx}px, ${vy + 200}px) rotate(${360 + Math.random() * 360}deg)`,
        opacity: 0,
      },
    ], {
      duration: 1000 + Math.random() * 500,
      easing: 'cubic-bezier(0, 0.5, 0.5, 1)',
    })

    container.appendChild(confetti)
  }

  setTimeout(() => container.remove(), 2000)
}
