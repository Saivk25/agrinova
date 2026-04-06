import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Text, View, ActivityIndicator } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { useStore } from './src/store/useStore';
import LoginScreen from './src/screens/LoginScreen';
import OnboardingScreen from './src/screens/OnboardingScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import MapScreen, { DocumentsScreen, AlertsScreen, SettingsScreen } from './src/screens/MapScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

function TabIcon({ name, focused }:{ name:string; focused:boolean }) {
  const icons:Record<string,string> = { Dashboard:'📊', Map:'🗺️', Documents:'📄', Alerts:'🔔', Settings:'⚙️' };
  return <Text style={{ fontSize:20, opacity:focused?1:0.5 }}>{icons[name]||'•'}</Text>;
}

function MainTabs() {
  return (
    <Tab.Navigator screenOptions={({ route }) => ({
      tabBarIcon:({ focused })=><TabIcon name={route.name} focused={focused}/>,
      tabBarActiveTintColor:'#2d6a4f', tabBarInactiveTintColor:'#aaa',
      headerShown:false, tabBarStyle:{paddingBottom:8,height:60}, tabBarLabelStyle:{fontSize:11},
    })}>
      <Tab.Screen name="Dashboard" component={DashboardScreen}/>
      <Tab.Screen name="Map" component={MapScreen}/>
      <Tab.Screen name="Documents" component={DocumentsScreen}/>
      <Tab.Screen name="Alerts" component={AlertsScreen}/>
      <Tab.Screen name="Settings" component={SettingsScreen}/>
    </Tab.Navigator>
  );
}

export default function App() {
  const { user } = useStore();
  const [loading, setLoading] = useState(true);
  useEffect(()=>{ setLoading(false); },[]);
  if(loading) return (
    <View style={{flex:1,justifyContent:'center',alignItems:'center',backgroundColor:'#f0f4f0'}}>
      <ActivityIndicator size="large" color="#2d6a4f"/>
      <Text style={{marginTop:12,color:'#2d6a4f',fontSize:16}}>Landroid</Text>
    </View>
  );
  return (
    <GestureHandlerRootView style={{flex:1}}>
      <SafeAreaProvider>
        <NavigationContainer>
          <Stack.Navigator screenOptions={{headerShown:false}}>
            {!user ? (
              <>
                <Stack.Screen name="Login" component={LoginScreen}/>
                <Stack.Screen name="Onboarding" component={OnboardingScreen}/>
              </>
            ) : (
              <Stack.Screen name="Main" component={MainTabs}/>
            )}
          </Stack.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
