import { Route, Switch, Redirect } from 'react-router-dom'
import { useSelector } from 'react-redux';


import {publicRoutes, privateRoutes} from './routes'

const AppRouter = (props) => {
    const auth = useSelector(state => state.authReducer.auth);
    //console.log('stylefromparent', props.style);
    console.log('auth', auth);
    return (
        auth ?
            <Switch>
                <div className={props.style}>
                    {
                        publicRoutes.map(route => {
                            console.log('route', route);
                            return (
                                <Route 
                                component={route.component}
                                path={route.path}
                                exact={route.exact}
                                key={route.path}
                                />
                            )
                        }
                        )
                    }
                    
                </div>

            </Switch>
            :
            <Switch>
                <div className={props.style}>
                    {
                    privateRoutes.map(route =>
                        <Route 
                            component={route.component}
                            path={route.path}
                            exact={route.exact}
                            key={route.path}
                        />
                    )
                    }
                     <Redirect to='/auth'/>
                </div>
                // <Redirect to='/auth'/>
            </Switch>
    );
}
export default AppRouter