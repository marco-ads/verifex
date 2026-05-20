import { memo } from 'react'

interface Props {
  lang: 'es' | 'en'
  onToggle: () => void
}

const LanguageToggle = memo(function LanguageToggle({ lang, onToggle }: Props) {
  return (
    <button className="toggle-btn" onClick={onToggle}>
      {lang === 'es' ? 'EN' : 'ES'}
    </button>
  )
})

export default LanguageToggle
