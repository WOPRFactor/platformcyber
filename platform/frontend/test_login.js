// Script para probar login desde la consola del navegador
// Copia y pega esto en la consola del navegador cuando estés en la página de login

async function testLogin() {
  console.log('🧪 Probando login...');
  
  const credentials = {
    username: 'admin',
    password: 'admin123'
  };
  
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Login exitoso!');
      console.log('Tokens recibidos:', {
        access_token: data.access_token.substring(0, 20) + '...',
        refresh_token: data.refresh_token.substring(0, 20) + '...'
      });
      console.log('Usuario:', data.user);
      
      // Guardar tokens en localStorage
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      console.log('🔄 Recargando página...');
      window.location.reload();
    } else {
      console.error('❌ Error en login:', data.error);
    }
  } catch (error) {
    console.error('❌ Error de conexión:', error);
  }
}

// Ejecutar el test
testLogin();
