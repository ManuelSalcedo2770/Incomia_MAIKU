import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/styles.css';

export const BankingLandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [lastLogin, setLastLogin] = useState('');

  useEffect(() => {
    const now = new Date();
    setLastLogin(now.toLocaleString('es-MX', { 
      day: '2-digit', 
      month: 'short', 
      year: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    }));
  }, []);

  const handleIncomiaClick = () => {
    navigate('/dashboard');
  };

  return (
    <div className="bank-simulation">
      {/* Top-most red bar (auth/header) */}
      <header className="global-header">
        <div className="header-container">
          <div className="logo-area">
            <span className="brand-name">Banco</span>
          </div>
          
          <div className="header-tools">
            <div className="user-greeting">
              <span>Bienvenido, <strong>Roberto D.</strong></span>
              <span className="last-login">Último acceso: {lastLogin}</span>
            </div>
            <button className="icon-action" title="Mensajes">
              <i className="lucide-mail"></i>
            </button>
            <button className="icon-action" title="Configuración">
              <i className="lucide-settings"></i>
            </button>
            <button className="btn-logout">Cerrar sesión</button>
            
            {/* INCOMIA Plugin Extension */}
            <button className="plugin-incomia" onClick={handleIncomiaClick}>
              INCOMIA
            </button>
          </div>
        </div>
      </header>

      {/* Secondary navigation */}
      <nav className="main-nav">
        <div className="nav-container">
          <a href="#" className="nav-link active">Posición Global</a>
          <a href="#" className="nav-link">Cuentas</a>
          <a href="#" className="nav-link">Tarjetas</a>
          <a href="#" className="nav-link">Transferencias y Pagos</a>
          <a href="#" className="nav-link">Inversiones</a>
          <a href="#" className="nav-link">Ofertas para ti</a>
        </div>
      </nav>

      {/* Main Dashboard Area */}
      <main className="dashboard-wrapper">
        <div className="dashboard-grid">
          {/* Left Column: Products */}
          <div className="products-column">
            <section className="product-group">
              <div className="group-header">
                <h2>Cuentas</h2>
                <span className="total-group-balance">$ 124,500.00 MXN</span>
              </div>
              
              <div className="product-card">
                <div className="product-info">
                  <h3 className="product-name">Súper Cuenta Nómina</h3>
                  <span className="product-number">**** **** **** 1234</span>
                </div>
                <div className="product-balance">
                  <span className="balance-amount">$ 110,250.00</span>
                  <span className="balance-label">Saldo disponible</span>
                </div>
                <div className="product-actions">
                  <a href="#">Movimientos</a> | <a href="#">Transferir</a>
                </div>
              </div>

              <div className="product-card">
                <div className="product-info">
                  <h3 className="product-name">Cuenta Ahorro Inversión</h3>
                  <span className="product-number">**** **** **** 5678</span>
                </div>
                <div className="product-balance">
                  <span className="balance-amount">$ 14,250.00</span>
                  <span className="balance-label">Saldo disponible</span>
                </div>
                <div className="product-actions">
                  <a href="#">Movimientos</a> | <a href="#">Abonar</a>
                </div>
              </div>
            </section>

            <section className="product-group">
              <div className="group-header">
                <h2>Tarjetas de Crédito</h2>
              </div>
              
              <div className="product-card credit-card">
                <div className="product-info">
                  <h3 className="product-name">Tarjeta Crédito LikeU</h3>
                  <span className="product-number">**** **** **** 9012</span>
                </div>
                <div className="product-balance">
                  <span className="balance-label">Límite de crédito: $ 50,000.00</span>
                  <span className="balance-amount negative">$ 8,450.50</span>
                  <span className="balance-label">Saldo dispuesto</span>
                </div>
                <div className="product-actions">
                  <a href="#">Pagar tarjeta</a> | <a href="#">Estado de cuenta</a>
                </div>
              </div>
            </section>
          </div>

          {/* Right Column: Shortcuts & Promos */}
          <div className="side-column">
            <div className="widget">
              <h3>Atajos Rápidos</h3>
              <ul className="shortcut-list">
                <li><a href="#">Transferir a terceros</a></li>
                <li><a href="#">Pago de servicios</a></li>
                <li><a href="#">Recarga de celular</a></li>
                <li><a href="#">Constancia de intereses</a></li>
              </ul>
            </div>
            
            <div className="promo-widget">
              <div className="promo-content">
                <h4>Aprovecha tu Pre-Autorizado</h4>
                <p>Tienes un crédito personal de hasta <strong>$150,000 MXN</strong> a tasa preferencial.</p>
                <button className="btn-promo">Ver oferta</button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
