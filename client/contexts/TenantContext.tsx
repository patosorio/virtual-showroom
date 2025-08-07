"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

interface Tenant {
  id: string;
  name: string;
  slug: string;
  logo?: string;
  settings?: Record<string, any>;
}

interface TenantContextType {
  currentTenant: Tenant | null;
  availableTenants: Tenant[];
  switchTenant: (tenantId: string) => void;
  isLoading: boolean;
}

const TenantContext = createContext<TenantContextType | null>(null);

export function TenantProvider({ children }: { children: React.ReactNode }) {
  const [currentTenant, setCurrentTenant] = useState<Tenant | null>(null);
  const [availableTenants, setAvailableTenants] = useState<Tenant[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated && user) {
      // Fetch user's available tenants
      fetchAvailableTenants();
    } else {
      setCurrentTenant(null);
      setAvailableTenants([]);
    }
  }, [isAuthenticated, user]);

  const fetchAvailableTenants = async () => {
    try {
      setIsLoading(true);
      // TODO: Replace with actual API call
      // const response = await apiClient.get('/tenants/me');
      
      // Mock data for now
      const mockTenants: Tenant[] = [
        {
          id: '1',
          name: 'Acme Swimwear',
          slug: 'acme-swimwear',
          logo: '/placeholder.svg?height=40&width=40'
        }
      ];
      
      setAvailableTenants(mockTenants);
      
      // Set current tenant (from localStorage or first available)
      const savedTenantId = localStorage.getItem('selectedTenantId');
      const defaultTenant = savedTenantId 
        ? mockTenants.find(t => t.id === savedTenantId) || mockTenants[0]
        : mockTenants[0];
        
      setCurrentTenant(defaultTenant);
      
    } catch (error) {
      console.error('Failed to fetch tenants:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const switchTenant = (tenantId: string) => {
    const tenant = availableTenants.find(t => t.id === tenantId);
    if (tenant) {
      setCurrentTenant(tenant);
      localStorage.setItem('selectedTenantId', tenantId);
      // TODO: Refresh data for new tenant context
    }
  };

  const value: TenantContextType = {
    currentTenant,
    availableTenants,
    switchTenant,
    isLoading,
  };

  return (
    <TenantContext.Provider value={value}>
      {children}
    </TenantContext.Provider>
  );
}

export function useTenant() {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  return context;
}
