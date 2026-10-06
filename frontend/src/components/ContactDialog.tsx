import { useEffect, useRef, useState } from 'react'

interface ContactDialogProps {
  patientName: string
  onClose: () => void
  onSubmit: (contactedAt: string, note: string) => Promise<void>
}

export function ContactDialog({
  patientName,
  onClose,
  onSubmit,
}: ContactDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [note, setNote] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const dialog = dialogRef.current

    if (!dialog) {
      return
    }

    dialog.showModal()

    return () => {
      if (dialog.open) {
        dialog.close()
      }
    }
  }, [])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!note.trim()) {
      setError('Please enter a contact note.')
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      await onSubmit(new Date().toISOString(), note.trim())
      onClose()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to record the contact attempt.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <dialog
      ref={dialogRef}
      className="contact-dialog"
      aria-labelledby="contact-dialog-title"
      onCancel={onClose}
    >
      <div className="contact-dialog__content">
        <h2 id="contact-dialog-title">Record contact attempt</h2>

        <p>
          Record a follow-up contact attempt for{' '}
          <strong>{patientName}</strong>.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="contact-note">
              Contact note
            </label>

            <textarea
              id="contact-note"
              value={note}
              onChange={(event) => setNote(event.target.value)}
              rows={5}
              maxLength={1000}
              required
              autoFocus
              aria-describedby={
                error ? 'contact-error' : 'contact-note-help'
              }
            />

            <span id="contact-note-help" className="form-help">
              Record the outcome of the contact attempt.
            </span>
          </div>

          {error && (
            <p
              id="contact-error"
              className="form-error"
              role="alert"
            >
              {error}
            </p>
          )}

          <div className="contact-dialog__actions">
            <button
              type="button"
              className="button button--secondary"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="button button--primary"
              disabled={submitting}
            >
              {submitting ? 'Saving…' : 'Record contact'}
            </button>
          </div>
        </form>
      </div>
    </dialog>
  )
}