import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Truck, Flame, MapPin, Users, Shield, Clock, ArrowRight, Zap } from 'lucide-react';

interface LandingPageProps {
  onRoleSelect: (role: 'customer' | 'driver' | 'dispatcher') => void;
}

export function LandingPage({ onRoleSelect }: LandingPageProps) {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden min-h-screen flex items-center">
        <div className="absolute inset-0">
          <ImageWithFallback
            src="https://images.unsplash.com/photo-1668010097829-8b85e244b894?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxvaWwlMjBlbmVyZ3klMjBpbmR1c3RyaWFsfGVufDF8fHx8MTc1ODk2NTEzNXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
            alt="Industrial Energy Background"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-br from-black/90 via-black/70 to-black/40"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-primary/20 via-transparent to-accent/10"></div>
          {/* Animated gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-accent/10 animate-pulse"></div>
        </div>
        
        <div className="relative z-10 container mx-auto px-4 py-8">
          <div className="text-center">
            {/* Brand Logo */}
            <div className="flex items-center justify-center gap-3 mb-8">
              <div className="relative">
                <Flame className="w-12 h-12 md:w-16 md:h-16 text-primary drop-shadow-lg" />
                <div className="absolute inset-0 w-12 h-12 md:w-16 md:h-16 bg-primary/20 rounded-full blur-xl"></div>
              </div>
              <div className="text-center">
                <span className="text-3xl md:text-5xl font-bold bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                  Ugunja
                </span>
                <div className="text-xs md:text-sm text-muted-foreground tracking-wider">
                  LPG FLEET MANAGEMENT
                </div>
              </div>
            </div>
            
            <h1 className="text-3xl md:text-5xl lg:text-7xl font-bold mb-6 leading-tight">
              Smart LPG Delivery
              <span className="block text-transparent bg-gradient-to-r from-primary via-accent to-primary bg-clip-text mt-2">
                Made Simple
              </span>
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
              Revolutionize your LPG operations with intelligent tracking, automated dispatch, 
              and real-time fleet management. Choose your role to get started.
            </p>
            
            {/* Role Selection Cards - Mobile First */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 max-w-4xl mx-auto mb-8">
              {/* Customer Card */}
              <Card 
                className="group border-border/50 bg-gradient-to-br from-card/90 to-primary/5 backdrop-blur-sm hover:from-primary/10 hover:to-accent/10 transition-all duration-500 cursor-pointer transform hover:scale-105 hover:shadow-2xl hover:shadow-primary/20"
                onClick={() => onRoleSelect('customer')}
              >
                <CardContent className="p-6 md:p-8 text-center">
                  <div className="relative mb-6">
                    <div className="w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-primary/20 to-accent/20 rounded-2xl flex items-center justify-center mb-4 mx-auto group-hover:from-primary/30 group-hover:to-accent/30 transition-all duration-300">
                      <Users className="w-8 h-8 md:w-10 md:h-10 text-primary group-hover:scale-110 transition-transform duration-300" />
                    </div>
                    <div className="absolute inset-0 w-16 h-16 md:w-20 md:h-20 bg-primary/10 rounded-2xl blur-xl group-hover:bg-primary/20 transition-all duration-300 mx-auto"></div>
                  </div>
                  <h3 className="text-xl md:text-2xl font-bold mb-3 group-hover:text-primary transition-colors duration-300">Customer</h3>
                  <p className="text-sm md:text-base text-muted-foreground mb-6 leading-relaxed">
                    Order LPG deliveries, track your shipments in real-time, and manage your supply needs efficiently.
                  </p>
                  <div className="flex items-center justify-center gap-2 text-primary group-hover:gap-3 transition-all duration-300">
                    <span className="text-sm font-medium">Get Started</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
                  </div>
                </CardContent>
              </Card>

              {/* Driver Card */}
              <Card 
                className="group border-border/50 bg-gradient-to-br from-card/90 to-accent/5 backdrop-blur-sm hover:from-accent/10 hover:to-primary/10 transition-all duration-500 cursor-pointer transform hover:scale-105 hover:shadow-2xl hover:shadow-accent/20"
                onClick={() => onRoleSelect('driver')}
              >
                <CardContent className="p-6 md:p-8 text-center">
                  <div className="relative mb-6">
                    <div className="w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-accent/20 to-primary/20 rounded-2xl flex items-center justify-center mb-4 mx-auto group-hover:from-accent/30 group-hover:to-primary/30 transition-all duration-300">
                      <Truck className="w-8 h-8 md:w-10 md:h-10 text-accent group-hover:scale-110 transition-transform duration-300" />
                    </div>
                    <div className="absolute inset-0 w-16 h-16 md:w-20 md:h-20 bg-accent/10 rounded-2xl blur-xl group-hover:bg-accent/20 transition-all duration-300 mx-auto"></div>
                  </div>
                  <h3 className="text-xl md:text-2xl font-bold mb-3 group-hover:text-accent transition-colors duration-300">Driver</h3>
                  <p className="text-sm md:text-base text-muted-foreground mb-6 leading-relaxed">
                    Manage your delivery routes, update order statuses, and communicate with dispatch seamlessly.
                  </p>
                  <div className="flex items-center justify-center gap-2 text-accent group-hover:gap-3 transition-all duration-300">
                    <span className="text-sm font-medium">Get Started</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
                  </div>
                </CardContent>
              </Card>

              {/* Dispatcher Card */}
              <Card 
                className="group border-border/50 bg-gradient-to-br from-card/90 to-primary/5 backdrop-blur-sm hover:from-primary/10 hover:to-accent/10 transition-all duration-500 cursor-pointer transform hover:scale-105 hover:shadow-2xl hover:shadow-primary/20"
                onClick={() => onRoleSelect('dispatcher')}
              >
                <CardContent className="p-6 md:p-8 text-center">
                  <div className="relative mb-6">
                    <div className="w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-primary/20 to-accent/20 rounded-2xl flex items-center justify-center mb-4 mx-auto group-hover:from-primary/30 group-hover:to-accent/30 transition-all duration-300">
                      <Zap className="w-8 h-8 md:w-10 md:h-10 text-primary group-hover:scale-110 transition-transform duration-300" />
                    </div>
                    <div className="absolute inset-0 w-16 h-16 md:w-20 md:h-20 bg-primary/10 rounded-2xl blur-xl group-hover:bg-primary/20 transition-all duration-300 mx-auto"></div>
                  </div>
                  <h3 className="text-xl md:text-2xl font-bold mb-3 group-hover:text-primary transition-colors duration-300">Dispatcher</h3>
                  <p className="text-sm md:text-base text-muted-foreground mb-6 leading-relaxed">
                    Control fleet operations, assign drivers, monitor deliveries, and optimize route efficiency.
                  </p>
                  <div className="flex items-center justify-center gap-2 text-primary group-hover:gap-3 transition-all duration-300">
                    <span className="text-sm font-medium">Get Started</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Additional CTA */}
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-4">
                New to Ugunja? Experience the future of LPG fleet management
              </p>
              <Button 
                variant="outline" 
                size="lg" 
                className="text-base px-6 py-3 border-primary/50 hover:bg-primary/10 hover:border-primary/70 transition-all duration-300"
              >
                Watch Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12 md:py-20 bg-gradient-to-b from-background via-card/20 to-background relative overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-transparent to-accent/20"></div>
        </div>
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center mb-12 md:mb-16">
            <h2 className="text-2xl md:text-4xl font-bold mb-4">
              Why Choose 
              <span className="block md:inline text-transparent bg-gradient-to-r from-primary to-accent bg-clip-text ml-2">
                Ugunja?
              </span>
            </h2>
            <p className="text-base md:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Experience the next generation of LPG fleet management with cutting-edge technology 
              designed for efficiency, safety, and growth.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
            <Card className="border-border/50 bg-gradient-to-br from-card/90 to-primary/5 backdrop-blur-sm hover:from-primary/10 hover:to-accent/5 transition-all duration-500 group">
              <CardContent className="p-6 md:p-8">
                <div className="relative mb-6">
                  <div className="w-12 h-12 md:w-16 md:h-16 bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                    <MapPin className="w-6 h-6 md:w-8 md:h-8 text-primary-foreground" />
                  </div>
                  <div className="absolute inset-0 w-12 h-12 md:w-16 md:h-16 bg-primary/20 rounded-2xl blur-lg group-hover:bg-primary/30 transition-all duration-300"></div>
                </div>
                <h3 className="text-lg md:text-2xl font-bold mb-3 md:mb-4 group-hover:text-primary transition-colors duration-300">
                  Live GPS Tracking
                </h3>
                <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                  Real-time location monitoring with precision GPS tracking. Monitor every delivery 
                  from dispatch to completion with live updates.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border/50 bg-gradient-to-br from-card/90 to-accent/5 backdrop-blur-sm hover:from-accent/10 hover:to-primary/5 transition-all duration-500 group">
              <CardContent className="p-6 md:p-8">
                <div className="relative mb-6">
                  <div className="w-12 h-12 md:w-16 md:h-16 bg-gradient-to-br from-accent to-primary rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Zap className="w-6 h-6 md:w-8 md:h-8 text-accent-foreground" />
                  </div>
                  <div className="absolute inset-0 w-12 h-12 md:w-16 md:h-16 bg-accent/20 rounded-2xl blur-lg group-hover:bg-accent/30 transition-all duration-300"></div>
                </div>
                <h3 className="text-lg md:text-2xl font-bold mb-3 md:mb-4 group-hover:text-accent transition-colors duration-300">
                  AI-Powered Dispatch
                </h3>
                <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                  Intelligent routing and driver assignment using machine learning algorithms. 
                  Optimize delivery times and fuel efficiency automatically.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border/50 bg-gradient-to-br from-card/90 to-primary/5 backdrop-blur-sm hover:from-primary/10 hover:to-accent/5 transition-all duration-500 group">
              <CardContent className="p-6 md:p-8">
                <div className="relative mb-6">
                  <div className="w-12 h-12 md:w-16 md:h-16 bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Shield className="w-6 h-6 md:w-8 md:h-8 text-primary-foreground" />
                  </div>
                  <div className="absolute inset-0 w-12 h-12 md:w-16 md:h-16 bg-primary/20 rounded-2xl blur-lg group-hover:bg-primary/30 transition-all duration-300"></div>
                </div>
                <h3 className="text-lg md:text-2xl font-bold mb-3 md:mb-4 group-hover:text-primary transition-colors duration-300">
                  Safety Compliance
                </h3>
                <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                  Comprehensive safety protocols with digital compliance tracking. 
                  Ensure regulatory adherence and secure LPG handling at every step.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gradient-to-t from-card/80 to-background border-t border-border/50 py-8 md:py-12">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="relative">
              <Flame className="w-6 h-6 text-primary" />
              <div className="absolute inset-0 w-6 h-6 bg-primary/20 rounded-full blur-lg"></div>
            </div>
            <span className="text-lg md:text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Ugunja
            </span>
          </div>
          <p className="text-sm md:text-base text-muted-foreground">
            Revolutionizing LPG delivery and fleet management for the modern world
          </p>
          <div className="mt-4 text-xs text-muted-foreground/60">
            © 2024 Ugunja. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}