import { Link } from 'react-router-dom'

export function Wordmark() {
  return (
    <Link to="/" className="brand-lockup">
      <svg viewBox="0 0 36 28" width="32" height="25" aria-hidden="true">
        <path
          fill="currentColor"
          d="M2 26V12l6-6 6 6v14H2zm2-2h8V13.2L8 8.4 4 13.2V24zm16 2V12l6-6 6 6v14H20zm2-2h8V13.2L26 8.4 22 13.2V24z"
        />
      </svg>
      <span className="brand-type">
        <span className="wordmark-name">MIKE</span>
        <span className="wordmark-role">BALI GUIDE</span>
      </span>
    </Link>
  )
}
