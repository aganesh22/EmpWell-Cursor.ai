/// <reference types="vite/client" />

interface GoogleIdConfiguration {
  client_id: string;
  callback: (response: { credential: string }) => void;
  auto_select?: boolean;
  cancel_on_tap_outside?: boolean;
}

interface GoogleButtonConfiguration {
  theme?: 'outline' | 'filled_blue' | 'filled_black';
  size?: 'large' | 'medium' | 'small';
  text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin';
  shape?: 'rectangular' | 'pill' | 'circle' | 'square';
  logo_alignment?: 'left' | 'center';
  width?: string;
}

export class GoogleAuth {
  private static instance: GoogleAuth;
  private isInitialized = false;
  private clientId: string;

  private constructor() {
    this.clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";
  }

  public static getInstance(): GoogleAuth {
    if (!GoogleAuth.instance) {
      GoogleAuth.instance = new GoogleAuth();
    }
    return GoogleAuth.instance;
  }

  public async initialize(): Promise<void> {
    if (this.isInitialized) return;

    return new Promise((resolve, reject) => {
      if (!this.clientId) {
        console.warn("Google Client ID not configured");
        resolve();
        return;
      }

      // Load Google Identity Services script
      if (!document.querySelector('script[src*="accounts.google.com"]')) {
        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.async = true;
        script.defer = true;
        script.onload = () => {
          this.initializeGoogleId();
          this.isInitialized = true;
          resolve();
        };
        script.onerror = () => {
          console.error("Failed to load Google Identity Services");
          reject(new Error("Failed to load Google Identity Services"));
        };
        document.head.appendChild(script);
      } else {
        this.initializeGoogleId();
        this.isInitialized = true;
        resolve();
      }
    });
  }

  private initializeGoogleId(): void {
    if (!window.google?.accounts?.id) {
      console.error("Google Identity Services not available");
      return;
    }

    window.google.accounts.id.initialize({
      client_id: this.clientId,
      callback: this.handleCredentialResponse.bind(this),
      auto_select: false,
      cancel_on_tap_outside: true,
    });
  }

  private handleCredentialResponse(response: { credential: string }): void {
    // Emit custom event with the credential
    const event = new CustomEvent('google-signin', {
      detail: { credential: response.credential }
    });
    window.dispatchEvent(event);
  }

  public renderSignInButton(
    element: HTMLElement,
    options: GoogleButtonConfiguration = {}
  ): void {
    if (!this.isInitialized || !window.google?.accounts?.id) {
      console.warn("Google Identity Services not initialized");
      return;
    }

    const defaultOptions: GoogleButtonConfiguration = {
      theme: 'outline',
      size: 'large',
      text: 'signin_with',
      shape: 'rectangular',
      logo_alignment: 'left',
    };

    window.google.accounts.id.renderButton(element, {
      ...defaultOptions,
      ...options,
    });
  }

  public promptSignIn(): void {
    if (!this.isInitialized || !window.google?.accounts?.id) {
      console.warn("Google Identity Services not initialized");
      return;
    }
    window.google.accounts.id.prompt();
  }

  public disableAutoSelect(): void {
    if (!this.isInitialized || !window.google?.accounts?.id) {
      return;
    }
    window.google.accounts.id.disableAutoSelect();
  }

  public isConfigured(): boolean {
    return !!this.clientId;
  }
}