import React, { useState } from 'react'
import Header from './components/Header'
import Home from './pages/Home'
import Games from './pages/Games'
import FreeFire from './pages/FreeFire'
import Topup from './pages/Topup'
import Orders from './pages/Orders'
import Admin from './pages/Admin'
import QR from './pages/QR'

export default function App() {
  const [page, setPage] = useState('home')

  return (
    <div className="app-root">
      <Header onNav={setPage} />
      <div className="content">
        {page === 'home' && <Home onNav={setPage} />}
        {page === 'games' && <Games onNav={setPage} />}
        {page === 'freefire' && <FreeFire onNav={setPage} />}
        {page === 'topup' && <Topup onNav={setPage} />}
        {page === 'orders' && <Orders onNav={setPage} />}
        {page === 'admin' && <Admin onNav={setPage} />}
        {page === 'qr' && <QR onNav={setPage} />}
      </div>
      <footer className="bottom-nav">
        <button onClick={() => setPage('home')}>Home</button>
        <button onClick={() => setPage('games')}>Games</button>
        <button onClick={() => setPage('orders')}>Orders</button>
        <button onClick={() => setPage('admin')}>Admin</button>
      </footer>
    </div>
  )
}
