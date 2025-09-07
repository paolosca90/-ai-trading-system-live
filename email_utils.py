import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

def send_registration_email(to_email, username):
    """
    Invia email di benvenuto con riepilogo dati di accesso usando Brevo SMTP
    """
    # Configurazione SMTP Brevo
    smtp_server = 'smtp-relay.brevo.com'
    smtp_port = 587
    smtp_username = '967997001@smtp-brevo.com'
    
    # Password SMTP da variabile d'ambiente o hardcoded per test
    smtp_password = os.getenv('BREVO_SMTP_PASSWORD', 'b8QxjJG4HUzw7DsA')
    
    # Email mittente personalizzata (deve essere verificata su Brevo)
    from_email = os.getenv('FROM_EMAIL', 'support@cash-revolution.com')  # Sostituisci con la tua email
    
    # Calcola data scadenza trial
    trial_end_date = (datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y')
    
    # Crea il messaggio
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = '🚀 AI Cash-Revolution - I tuoi dati di accesso sono pronti!'
    
    # Corpo dell'email HTML
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #0a0a0a; color: #e0e0e0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1a1a1a, #2d2d2d); border: 2px solid #00ff41; border-radius: 15px; padding: 30px;">
            
            <h1 style="color: #00ff41; text-align: center; font-size: 24px; margin-bottom: 20px;">
                🎯 Benvenuto su AI Cash-Revolution!
            </h1>
            
            <p style="font-size: 16px; line-height: 1.6;">
                Ciao <strong style="color: #00ff41;">{username}</strong>,
            </p>
            
            <p style="font-size: 16px; line-height: 1.6;">
                La tua registrazione è stata completata con successo! 
                Il tuo <strong>trial gratuito di 7 giorni</strong> è ora attivo.
            </p>
            
            <!-- RIEPILOGO DATI DI ACCESSO -->
            <div style="background-color: #1a1a1a; border: 2px solid #00ff41; border-radius: 8px; padding: 20px; margin: 25px 0;">
                <h3 style="color: #00ff41; margin-top: 0; text-align: center;">🔑 I TUOI DATI DI ACCESSO</h3>
                
                <table style="width: 100%; color: #e0e0e0; font-size: 14px;">
                    <tr>
                        <td style="padding: 8px; font-weight: bold; color: #00ff41;">Username:</td>
                        <td style="padding: 8px; background-color: #2d2d2d; border-radius: 4px;"><strong>{username}</strong></td>
                    </tr>
                    <tr><td colspan="2" style="padding: 4px;"></td></tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold; color: #00ff41;">Email:</td>
                        <td style="padding: 8px; background-color: #2d2d2d; border-radius: 4px;"><strong>{to_email}</strong></td>
                    </tr>
                    <tr><td colspan="2" style="padding: 4px;"></td></tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold; color: #00ff41;">Password:</td>
                        <td style="padding: 8px; background-color: #2d2d2d; border-radius: 4px;">La password che hai scelto durante la registrazione</td>
                    </tr>
                    <tr><td colspan="2" style="padding: 4px;"></td></tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold; color: #00ff41;">Status Account:</td>
                        <td style="padding: 8px; background-color: #2d2d2d; border-radius: 4px;"><span style="color: #00ff41; font-weight: bold;">TRIAL ATTIVO</span></td>
                    </tr>
                    <tr><td colspan="2" style="padding: 4px;"></td></tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold; color: #00ff41;">Trial scade il:</td>
                        <td style="padding: 8px; background-color: #2d2d2d; border-radius: 4px;"><strong>{trial_end_date}</strong></td>
                    </tr>
                </table>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://your-domain.up.railway.app/dashboard.html" 
                   style="display: inline-block; background: linear-gradient(90deg, #00ff41, #00cc33); color: #000; text-decoration: none; padding: 15px 35px; border-radius: 25px; font-weight: bold; font-size: 18px; text-transform: uppercase;">
                    🚀 ACCEDI ORA ALLA DASHBOARD
                </a>
            </div>
            
            <div style="background-color: #1a1a1a; border: 1px solid #00ff41; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="color: #00ff41; margin-top: 0;">✅ Cosa puoi fare da subito:</h3>
                <ul style="padding-left: 20px; line-height: 1.8;">
                    <li><strong>Ricevere segnali AI</strong> in tempo reale</li>
                    <li><strong>Monitorare performance</strong> degli algoritmi</li>
                    <li><strong>Configurare MT5</strong> per trading automatico</li>
                    <li><strong>Scaricare Expert Advisor</strong> personalizzato</li>
                    <li><strong>Accesso completo</strong> a tutte le funzionalità Premium</li>
                </ul>
            </div>
            
            <!-- LINK RAPIDI -->
            <div style="background-color: #2d2d2d; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <h4 style="color: #00ff41; margin-top: 0;">🔗 Link Rapidi:</h4>
                <p style="margin: 8px 0;">
                    📊 <a href="https://your-domain.up.railway.app/dashboard.html" style="color: #00ff41; text-decoration: none;">Dashboard Principale</a>
                </p>
                <p style="margin: 8px 0;">
                    📈 <a href="https://your-domain.up.railway.app/signals.html" style="color: #00ff41; text-decoration: none;">Segnali Live</a>
                </p>
                <p style="margin: 8px 0;">
                    ⚙️ <a href="https://your-domain.up.railway.app/mt5-integration.html" style="color: #00ff41; text-decoration: none;">Configurazione MT5</a>
                </p>
                <p style="margin: 8px 0;">
                    👤 <a href="https://your-domain.up.railway.app/profile.html" style="color: #00ff41; text-decoration: none;">Profilo Utente</a>
                </p>
            </div>
            
            <p style="font-size: 14px; line-height: 1.6; color: #cccccc; background-color: #1a1a1a; padding: 15px; border-radius: 8px;">
                <strong style="color: #00ff41;">📞 Supporto Clienti:</strong><br>
                • Email: <a href="mailto:{from_email}" style="color: #00ff41;">{from_email}</a><br>
                • Risposta entro 2 ore (lun-ven 9-18)<br>
                • Per supporto tecnico, includi sempre il tuo username
            </p>
            
            <hr style="border: none; border-top: 1px solid #333; margin: 20px 0;">
            
            <p style="text-align: center; font-size: 12px; color: #888;">
                <strong>AI Cash-Revolution</strong> - Trading Automatizzato<br>
                Account creato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}<br>
                Questa email è stata inviata automaticamente.
            </p>
        </div>
    </body>
    </html>
    """
    
    # Versione testo semplice (fallback)
    text_body = f"""
=== AI CASH-REVOLUTION - DATI DI ACCESSO ===

Ciao {username},

La tua registrazione è stata completata con successo!

I TUOI DATI DI ACCESSO:
• Username: {username}
• Email: {to_email}
• Password: La password che hai scelto durante la registrazione
• Status: TRIAL ATTIVO (scade il {trial_end_date})

ACCEDI ALLA DASHBOARD:
https://your-domain.up.railway.app/dashboard.html

COSA PUOI FARE SUBITO:
• Ricevere segnali AI in tempo reale
• Monitorare performance degli algoritmi
• Configurare MT5 per trading automatico
• Scaricare Expert Advisor personalizzato

LINK RAPIDI:
• Dashboard: https://your-domain.up.railway.app/dashboard.html
• Segnali Live: https://your-domain.up.railway.app/signals.html
• MT5: https://your-domain.up.railway.app/mt5-integration.html
• Profilo: https://your-domain.up.railway.app/profile.html

SUPPORTO:
Email: {from_email}
Risposta entro 2 ore (lun-ven 9-18)

Buon trading!
Lo staff di AI Cash-Revolution

Account creato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}
    """
    
    # Aggiungi entrambe le versioni
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        # Connessione SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        # Invia email
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        
        print(f"✅ Email di benvenuto con dati di accesso inviata a {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Errore invio email a {to_email}: {str(e)}")
        return False

def send_password_reset_email(to_email, username, reset_token):
    """
    Invia email per reset password (per uso futuro)
    """
    # TODO: Implementare reset password
    pass

