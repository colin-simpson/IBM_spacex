# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['PayloadMassKG'].max()
min_payload = spacex_df['PayloadMassKG'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
        html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
        
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(['ALL', 'CCAFS LC-40', 'CCAFS SLC-40', 'VAFB SLC-4E', 'KSC LC-39A'], 'ALL', id='site-dropdown'),
        
        html.Br(),

        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id='success-pie-chart')),
        
        html.Br(),

        html.P("Payload range (Kg):"),

        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(min_payload, max_payload, value=[min_payload, max_payload], id='payload-slider'),

        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),
        ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')    
)

def get_pie_chart(launch_site):

    # show total successful launches count for all sites
    if launch_site == 'ALL':
        launch_site_df = spacex_df.groupby('LaunchSite')['Class'].sum().reset_index()
        launch_site_df = launch_site_df.rename(columns={'Class': 'Count'})
        print('DEBUG\n', launch_site_df.head(),'\nDEBUG\n')
        fig = px.pie(launch_site_df, values='Count', names='LaunchSite', title='Successful launches for each site')

    # show the Success vs. Failed counts for the specific site
    else:
        site_missions = spacex_df[spacex_df['LaunchSite'] == launch_site]
        count_success = len(site_missions[site_missions['Class'] == 1])
        count_fail = len(site_missions[site_missions['Class'] == 0])
        counts_df = pd.DataFrame({'Outcome': ['Failure', 'Success'], 'Count': [count_fail, count_success]})
        fig = px.pie(counts_df, values='Count', names='Outcome', color_discrete_map={'Failure':'red', 'Success':'blue'}, title='Fail vs Success launches at site '+launch_site)
    
    # return our created pie chart
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)

def get_scatter_chart(launch_site, payload_range):
    if launch_site == 'ALL':
        site_missions = spacex_df[(spacex_df['PayloadMassKG'] >= payload_range[0]) & (spacex_df['PayloadMassKG'] <= payload_range[1])]
        fig = px.scatter(site_missions, x='PayloadMassKG', y='Class', color='BoosterVersionCategory', title='Correlation between payload and launch success at site: '+launch_site)
    else:
        site_missions = spacex_df[(spacex_df['LaunchSite'] == launch_site) & (spacex_df['PayloadMassKG'] >= payload_range[0]) & (spacex_df['PayloadMassKG'] <= payload_range[1])]
        fig = px.scatter(site_missions, x='PayloadMassKG', y='Class', title='Correlation between payload and launch success at site: '+launch_site)
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()