import { useState } from 'react';

interface PopupState {
  open: boolean;
  ticker: string;
  indicator: string;
}

export function useIndicatorPopup() {
  const [state, setState] = useState<PopupState>({ open: false, ticker: '', indicator: '' });

  const openPopup = (ticker: string, indicator: string) =>
    setState({ open: true, ticker, indicator });

  const closePopup = () =>
    setState(s => ({ ...s, open: false }));

  return { ...state, openPopup, closePopup };
}
