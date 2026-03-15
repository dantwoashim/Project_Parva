import { useContext } from 'react';
import { MemberContext } from './memberContextShared';

export function useMemberContext() {
  const value = useContext(MemberContext);
  if (!value) {
    throw new Error('useMemberContext must be used within a MemberProvider');
  }
  return value;
}
