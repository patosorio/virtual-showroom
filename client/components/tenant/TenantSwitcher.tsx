"use client";

import React from 'react';
import { ChevronDown, Building2 } from 'lucide-react';
import { useTenant } from '@/contexts/TenantContext';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export function TenantSwitcher() {
  const { currentTenant, availableTenants, switchTenant, isLoading } = useTenant();

  if (isLoading || !currentTenant || availableTenants.length <= 1) {
    return (
      <div className="flex items-center px-3 py-2 text-sm">
        <Building2 className="mr-2 h-4 w-4" />
        {currentTenant?.name || 'Loading...'}
      </div>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="w-full justify-start px-3 py-2 text-sm">
          <Building2 className="mr-2 h-4 w-4" />
          {currentTenant.name}
          <ChevronDown className="ml-auto h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        {availableTenants.map((tenant) => (
          <DropdownMenuItem
            key={tenant.id}
            onClick={() => switchTenant(tenant.id)}
            className={currentTenant.id === tenant.id ? 'bg-gray-100' : ''}
          >
            <Building2 className="mr-2 h-4 w-4" />
            {tenant.name}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}