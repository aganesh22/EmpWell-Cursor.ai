/// <reference types="vite/client" />
import { 
  PublicClientApplication, 
  Configuration, 
  AccountInfo, 
  AuthenticationResult,
  SilentRequest,
  RedirectRequest,
  PopupRequest
} from '@azure/msal-browser';

export interface AzureAuthConfig {
  clientId: string;
  authority: string;
  redirectUri: string;
  scopes: string[];
}

export class AzureAuth {
  private static instance: AzureAuth;
  private msalInstance: PublicClientApplication | null = null;
  private isInitialized = false;
  private config: AzureAuthConfig;

  private constructor() {
    this.config = {
      clientId: import.meta.env.VITE_AZURE_CLIENT_ID || "",
      authority: import.meta.env.VITE_AZURE_AUTHORITY || "https://login.microsoftonline.com/common",
      redirectUri: import.meta.env.VITE_AZURE_REDIRECT_URI || window.location.origin,
      scopes: ["openid", "profile", "User.Read", "email"]
    };
  }

  public static getInstance(): AzureAuth {
    if (!AzureAuth.instance) {
      AzureAuth.instance = new AzureAuth();
    }
    return AzureAuth.instance;
  }

  public async initialize(): Promise<void> {
    if (this.isInitialized || !this.isConfigured()) {
      return;
    }

    const msalConfig: Configuration = {
      auth: {
        clientId: this.config.clientId,
        authority: this.config.authority,
        redirectUri: this.config.redirectUri,
        postLogoutRedirectUri: this.config.redirectUri,
        navigateToLoginRequestUrl: false
      },
      cache: {
        cacheLocation: "sessionStorage",
        storeAuthStateInCookie: false,
      },
      system: {
        loggerOptions: {
          loggerCallback: (level, message, containsPii) => {
            if (containsPii) return;
            switch (level) {
              case 0: // Error
                console.error('[MSAL Error]', message);
                break;
              case 1: // Warning  
                console.warn('[MSAL Warning]', message);
                break;
              case 2: // Info
                console.info('[MSAL Info]', message);
                break;
              case 3: // Verbose
                console.log('[MSAL Verbose]', message);
                break;
            }
          }
        }
      }
    };

    try {
      this.msalInstance = new PublicClientApplication(msalConfig);
      await this.msalInstance.initialize();
      
      // Handle redirect promise
      const response = await this.msalInstance.handleRedirectPromise();
      if (response) {
        this.handleAuthResponse(response);
      }
      
      this.isInitialized = true;
      console.log('[Azure Auth] Initialized successfully');
    } catch (error) {
      console.error('[Azure Auth] Initialization failed:', error);
      throw error;
    }
  }

  public async loginPopup(): Promise<AuthenticationResult | null> {
    if (!this.msalInstance) {
      throw new Error('MSAL instance not initialized');
    }

    const loginRequest: PopupRequest = {
      scopes: this.config.scopes,
      prompt: "select_account"
    };

    try {
      const response = await this.msalInstance.loginPopup(loginRequest);
      this.handleAuthResponse(response);
      return response;
    } catch (error) {
      console.error('[Azure Auth] Login popup failed:', error);
      throw error;
    }
  }

  public async loginRedirect(): Promise<void> {
    if (!this.msalInstance) {
      throw new Error('MSAL instance not initialized');
    }

    const loginRequest: RedirectRequest = {
      scopes: this.config.scopes,
      prompt: "select_account"
    };

    try {
      await this.msalInstance.loginRedirect(loginRequest);
    } catch (error) {
      console.error('[Azure Auth] Login redirect failed:', error);
      throw error;
    }
  }

  public async logout(): Promise<void> {
    if (!this.msalInstance) {
      throw new Error('MSAL instance not initialized');
    }

    try {
      await this.msalInstance.logoutPopup({
        postLogoutRedirectUri: this.config.redirectUri,
        mainWindowRedirectUri: this.config.redirectUri
      });
    } catch (error) {
      console.error('[Azure Auth] Logout failed:', error);
      throw error;
    }
  }

  public async getAccessToken(): Promise<string | null> {
    if (!this.msalInstance) {
      throw new Error('MSAL instance not initialized');
    }

    const accounts = this.msalInstance.getAllAccounts();
    if (accounts.length === 0) {
      return null;
    }

    const silentRequest: SilentRequest = {
      scopes: this.config.scopes,
      account: accounts[0]
    };

    try {
      const response = await this.msalInstance.acquireTokenSilent(silentRequest);
      return response.accessToken;
    } catch (error) {
      console.warn('[Azure Auth] Silent token acquisition failed:', error);
      
      try {
        // Fallback to popup
        const response = await this.msalInstance.acquireTokenPopup(silentRequest);
        return response.accessToken;
      } catch (popupError) {
        console.error('[Azure Auth] Token acquisition failed:', popupError);
        return null;
      }
    }
  }

  public getCurrentAccount(): AccountInfo | null {
    if (!this.msalInstance) {
      return null;
    }

    const accounts = this.msalInstance.getAllAccounts();
    return accounts.length > 0 ? accounts[0] : null;
  }

  public isAuthenticated(): boolean {
    if (!this.msalInstance) {
      return false;
    }

    const accounts = this.msalInstance.getAllAccounts();
    return accounts.length > 0;
  }

  public getUserInfo(): { email?: string; name?: string; jobTitle?: string; department?: string } | null {
    const account = this.getCurrentAccount();
    if (!account) {
      return null;
    }

    return {
      email: account.username,
      name: account.name || undefined,
      jobTitle: account.idTokenClaims?.jobTitle as string || undefined,
      department: account.idTokenClaims?.department as string || undefined
    };
  }

  public isConfigured(): boolean {
    return !!(this.config.clientId && this.config.authority);
  }

  private handleAuthResponse(response: AuthenticationResult): void {
    if (response.account) {
      console.log('[Azure Auth] Authentication successful:', response.account.username);
      
      // Emit custom event for the application to handle
      const event = new CustomEvent('azure-auth-success', {
        detail: {
          account: response.account,
          accessToken: response.accessToken,
          idToken: response.idToken
        }
      });
      window.dispatchEvent(event);
    }
  }

  public async getUserProfile(): Promise<any> {
    const token = await this.getAccessToken();
    if (!token) {
      throw new Error('No access token available');
    }

    try {
      const response = await fetch('https://graph.microsoft.com/v1.0/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Graph API request failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[Azure Auth] Failed to fetch user profile:', error);
      throw error;
    }
  }

  public async getUserPhoto(): Promise<string | null> {
    const token = await this.getAccessToken();
    if (!token) {
      return null;
    }

    try {
      const response = await fetch('https://graph.microsoft.com/v1.0/me/photo/$value', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        return null;
      }

      const blob = await response.blob();
      return URL.createObjectURL(blob);
    } catch (error) {
      console.warn('[Azure Auth] Failed to fetch user photo:', error);
      return null;
    }
  }
}