const API_CADASTRO_URL = 'http://localhost:8000/cadastro/';

// tudo em DOMContentLoaded para garantir que os elementos existem na funçao/ usuarios
document.addEventListener('DOMContentLoaded', function() {
    
    
    const botaoCriarConta = document.getElementById('botaoCriarConta');

    if (botaoCriarConta) {
        botaoCriarConta.addEventListener('click', enviarCadastro);
    }
    
    
    const passwordInput = document.getElementById('password');
    const toggle = document.getElementById('togglePassword');
    
    if (passwordInput && toggle) {
        toggle.addEventListener('click', function() {
            
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
          
            this.textContent = (type === 'password') ? '👁️' : '🔒'; 
        });
    }
});

function enviarCadastro(event) {
    event.preventDefault(); 
    
    
    const username = document.getElementById('usuario').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value; 

    if (!username || !email || !password) {
        alert('Por favor, preencha todos os campos obrigatórios.');
        return;
    }

    const dadosCadastro = {
        username: username,
        email: email,
        password: password
    };

    fetch(API_CADASTRO_URL, {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dadosCadastro) 
    })
    .then(response => {
        if (response.status === 201) {
           
            alert('✅ Conta criada com sucesso! Você pode logar agora.');
            
            window.location.href = '/'; 
            return;
        } else if (response.status === 400) {
            
            return response.json().then(data => {
                let errorMessage = 'Erros de validação:';
                
                for (const key in data) {
                    errorMessage += `\n- ${key}: ${data[key]}`;
                }
                alert(`❌ Erro no cadastro:\n${errorMessage}`);
            });
        } else {
            
            alert(`⚠️ Erro no servidor (Status: ${response.status}). Tente novamente mais tarde.`);
        }
    })
    .catch(error => {
        
        console.error('Erro de conexão:', error);
        alert('🚨 Falha ao conectar. Verifique se o servidor está rodando.');
    });
}