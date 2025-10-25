import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Flame, ArrowLeft, Eye, EyeOff, Users, Truck, Zap } from 'lucide-react';
import { authAPI } from '../lib/api';

interface AuthPageProps {
  selectedRole: 'customer' | 'driver' | 'dispatcher';
  onLogin: (user: any) => void;
  onBack: () => void;
}

export function AuthPage({ selectedRole, onLogin, onBack }: AuthPageProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: ''
  });
  const [registerForm, setRegisterForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'customer': return <Users className="w-5 h-5" />;
      case 'driver': return <Truck className="w-5 h-5" />;
      case 'dispatcher': return <Zap className="w-5 h-5" />;
      default: return <Users className="w-5 h-5" />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'customer': return 'text-primary';
      case 'driver': return 'text-accent';
      case 'dispatcher': return 'text-primary';
      default: return 'text-primary';
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await authAPI.login({
        email: loginForm.email,
        password: loginForm.password,
        role: selectedRole
      });

      console.log('Login response:', response);
      
      const user = {
        id: response.user.id.toString(),
        email: response.user.email,
        role: response.user.role,
        name: response.user.username,
        token: response.tokens.access_token
      };
      
      console.log('Final user object:', user);
      onLogin(user);
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (registerForm.password !== registerForm.confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      const response = await authAPI.register({
        name: registerForm.name,
        email: registerForm.email,
        password: registerForm.password,
        role: selectedRole
      });

      console.log('Register response:', response);
      
      const user = {
        id: response.user.id.toString(),
        email: response.user.email,
        role: response.user.role,
        name: response.user.username,
        token: response.tokens.access_token
      };
      
      console.log('Final user object:', user);
      onLogin(user);
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-card/20 to-background relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-accent/5"></div>
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/5 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-accent/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
      
      <div className="relative z-10 w-full max-w-md">
        <div className="mb-6 md:mb-8">
          <Button 
            variant="ghost" 
            onClick={onBack}
            className="mb-4 text-muted-foreground hover:text-foreground transition-colors duration-300"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
          
          {/* Brand Header */}
          <div className="text-center mb-6">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="relative">
                <Flame className="w-8 h-8 md:w-10 md:h-10 text-primary" />
                <div className="absolute inset-0 w-8 h-8 md:w-10 md:h-10 bg-primary/20 rounded-full blur-lg"></div>
              </div>
              <span className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Ugunja
              </span>
            </div>
            
            {/* Role Display */}
            <div className="flex items-center justify-center gap-2 px-4 py-2 bg-card/50 backdrop-blur-sm rounded-full border border-border/50">
              <div className={getRoleColor(selectedRole)}>
                {getRoleIcon(selectedRole)}
              </div>
              <span className="text-sm font-medium capitalize">{selectedRole} Portal</span>
            </div>
          </div>
        </div>

        <Card className="border-border/50 bg-card/90 backdrop-blur-sm shadow-2xl">
          <CardHeader className="text-center pb-6">
            <CardTitle className="text-xl md:text-2xl mb-2">Welcome Back</CardTitle>
            <p className="text-sm md:text-base text-muted-foreground">
              Sign in to access your {selectedRole} dashboard
            </p>
          </CardHeader>
          <CardContent className="p-4 md:p-6">
            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2 mb-6 bg-muted/50">
                <TabsTrigger value="login" className="text-sm">Sign In</TabsTrigger>
                <TabsTrigger value="register" className="text-sm">Register</TabsTrigger>
              </TabsList>

              <TabsContent value="login">
                <form onSubmit={handleLogin} className="space-y-4 md:space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-sm">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email"
                      value={loginForm.email}
                      onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                      required
                      className="bg-background/50 border-border/50 focus:border-primary/50 h-11 text-sm"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-sm">Password</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        value={loginForm.password}
                        onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                        required
                        className="bg-background/50 border-border/50 focus:border-primary/50 pr-10 h-11 text-sm"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Eye className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    </div>
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full bg-gradient-to-r from-primary to-accent hover:from-accent hover:to-primary transition-all duration-300 h-11 text-sm"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Signing In...' : `Sign In as ${selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)}`}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="register">
                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-sm">Full Name</Label>
                    <Input
                      id="name"
                      type="text"
                      placeholder="Enter your full name"
                      value={registerForm.name}
                      onChange={(e) => setRegisterForm({...registerForm, name: e.target.value})}
                      required
                      className="bg-background/50 border-border/50 focus:border-primary/50 h-11 text-sm"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-email" className="text-sm">Email Address</Label>
                    <Input
                      id="register-email"
                      type="email"
                      placeholder="Enter your email"
                      value={registerForm.email}
                      onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                      required
                      className="bg-background/50 border-border/50 focus:border-primary/50 h-11 text-sm"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="register-password" className="text-sm">Password</Label>
                      <Input
                        id="register-password"
                        type="password"
                        placeholder="Create password"
                        value={registerForm.password}
                        onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
                        required
                        className="bg-background/50 border-border/50 focus:border-primary/50 h-11 text-sm"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="confirm-password" className="text-sm">Confirm Password</Label>
                      <Input
                        id="confirm-password"
                        type="password"
                        placeholder="Confirm password"
                        value={registerForm.confirmPassword}
                        onChange={(e) => setRegisterForm({...registerForm, confirmPassword: e.target.value})}
                        required
                        className="bg-background/50 border-border/50 focus:border-primary/50 h-11 text-sm"
                      />
                    </div>
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full bg-gradient-to-r from-primary to-accent hover:from-accent hover:to-primary transition-all duration-300 h-11 text-sm"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Creating Account...' : `Create ${selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)} Account`}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <div className="mt-4 md:mt-6 text-center">
          <div className="bg-card/30 backdrop-blur-sm border border-border/30 rounded-lg p-3 md:p-4">
            <p className="text-xs md:text-sm text-muted-foreground mb-2">
              <strong>Demo Mode:</strong> Use any email/password to continue
            </p>
            <p className="text-xs text-muted-foreground/80">
              Selected role: <span className={`font-medium ${getRoleColor(selectedRole)}`}>
                {selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)}
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}