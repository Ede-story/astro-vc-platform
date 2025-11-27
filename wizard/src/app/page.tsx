export default function JoinPage() {
  return (
    <main style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'system-ui, sans-serif',
      backgroundColor: '#0a0a0a',
      color: '#ffffff'
    }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
        StarMeet
      </h1>
      <p style={{ fontSize: '1.25rem', color: '#888', marginBottom: '2rem' }}>
        Wizard is loading...
      </p>
      <div style={{
        padding: '1rem 2rem',
        backgroundColor: '#1a1a1a',
        borderRadius: '8px',
        border: '1px solid #333'
      }}>
        <p>API: {process.env.NEXT_PUBLIC_API_URL}</p>
      </div>
    </main>
  );
}
