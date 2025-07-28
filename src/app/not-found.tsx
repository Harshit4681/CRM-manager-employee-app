// Custom 404 page that doesn't use Firebase
export default function NotFound() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      textAlign: 'center',
      padding: '20px'
    }}>
      <h1 style={{ fontSize: '4rem', margin: '0' }}>404</h1>
      <h2 style={{ fontSize: '1.5rem', margin: '20px 0' }}>Page Not Found</h2>
      <p style={{ fontSize: '1rem', color: '#666', marginBottom: '30px' }}>
        The page you are looking for does not exist.
      </p>
      <a 
        href="/login" 
        style={{
          padding: '10px 20px',
          backgroundColor: '#0070f3',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '5px',
          fontSize: '1rem'
        }}
      >
        Go to Login
      </a>
    </div>
  );
}