import React from 'react';
import { Link, Outlet } from 'react-router-dom';

export default function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-indigo-700 text-white p-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">Procurement System</h1>
        <nav className="space-x-4">
          <Link to="/" className="hover:underline">Dashboard</Link>
          <Link to="/products" className="hover:underline">Products</Link>
          <Link to="/inventory" className="hover:underline">Inventory</Link>
          <Link to="/purchase-orders" className="hover:underline">Purchase Orders</Link>
          <Link to="/suppliers" className="hover:underline">Suppliers</Link>
          <Link to="/shipments" className="hover:underline">Shipments</Link>
        </nav>
      </header>
      <main className="flex-1 p-6 bg-gray-50">
        <Outlet />
      </main>
    </div>
  );
} 