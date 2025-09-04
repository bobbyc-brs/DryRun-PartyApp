"""
Host interface routes for the Party Drink Tracker application.

This module contains all the Flask routes for the host interface, providing
monitoring capabilities for party hosts. The host interface runs on port 4001
and includes dashboard views, BAC calculations, and interactive charts showing
guest consumption patterns and estimated blood alcohol levels.

Copyright (C) 2025 Brighter Sight
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

For inquiries, contact: Info@BrighterSight.ca
"""

from flask import Blueprint, render_template, jsonify
from app.models import Guest, DrinkConsumption, Drink
from app.constants import (
    ETHANOL_DENSITY_G_PER_ML,
    LBS_TO_KG_CONVERSION,
    BAC_METABOLISM_RATE,
    AVERAGE_GENDER_CONSTANT,
    BAC_DISPLAY_CAP,
    BAC_DECIMAL_PRECISION,
    BAC_LEGAL_LIMIT
)
import plotly
import plotly.graph_objs as go
import json
from datetime import datetime, timedelta

host_bp = Blueprint('host', __name__, url_prefix='/host')

@host_bp.route('/', methods=['GET'])
def dashboard():
    """
    Display the host dashboard with guest consumption monitoring.
    
    This route renders the main host dashboard that shows all guests and their
    consumption data. The dashboard includes real-time BAC calculations and
    interactive charts for monitoring party safety.
    
    Returns:
        str: Rendered HTML template for the host dashboard.
    """
    guests = Guest.query.all()
    return render_template('host/dashboard.html', guests=guests)

@host_bp.route('/guest_data', methods=['GET'])
def guest_data():
    """
    API endpoint to get consumption data for all guests.
    
    This endpoint returns JSON data containing each guest's consumption information,
    including drink counts by type and current BAC levels. Used by the dashboard
    to display real-time consumption statistics.
    
    Returns:
        JSON: List of guest data with consumption statistics and BAC levels.
    """
    guests = Guest.query.all()
    data = []
    
    for guest in guests:
        # Count drinks by type
        drink_counts = {}
        for consumption in guest.drinks:
            drink_name = consumption.drink.name
            if drink_name in drink_counts:
                drink_counts[drink_name] += 1
            else:
                drink_counts[drink_name] = 1
        
        # Calculate BAC
        bac = guest.calculate_bac()
        
        # Get total drink count
        total_drinks = len(guest.drinks)
        
        data.append({
            'id': guest.id,
            'name': guest.name,
            'weight': guest.weight,
            'total_drinks': total_drinks,
            'drink_breakdown': drink_counts,
            'bac': bac
        })
    
    return jsonify(data)

@host_bp.route('/bac_chart/<int:guest_id>', methods=['GET'])
def bac_chart(guest_id):
    """
    Generate BAC chart data for a specific guest.
    
    This endpoint creates a Plotly chart showing the estimated BAC over time for
    a specific guest. The chart shows BAC levels over the past 6 hours at 15-minute
    intervals, including drink consumption markers.
    
    Args:
        guest_id (int): The ID of the guest to generate the chart for.
        
    Returns:
        JSON: Plotly chart configuration as JSON string.
    """
    guest = Guest.query.get_or_404(guest_id)
    
    if not guest.weight or guest.weight <= 0:
        return jsonify({'error': 'Guest weight not set'}), 400
    
    # Generate BAC timeline
    now = datetime.utcnow()
    start_time = now - timedelta(hours=6)  # Show 6 hours of history
    
    # Create timestamps at 15-minute intervals
    timestamps = []
    current = start_time
    while current <= now:
        timestamps.append(current)
        current += timedelta(minutes=15)
    
    # Calculate BAC at each timestamp
    bac_values = []
    
    for timestamp in timestamps:
        # Filter consumptions before this timestamp
        relevant_consumptions = [c for c in guest.drinks if c.timestamp <= timestamp]
        
        # Calculate BAC at this timestamp
        if not relevant_consumptions:
            bac_values.append(0)
            continue
        
        # Calculate total alcohol consumed before this timestamp
        total_alcohol_grams = 0

        for consumption in relevant_consumptions:
            drink = consumption.drink
            # Calculate alcohol in grams: ABV * volume(ml) * density of ethanol in g/ml / 100
            alcohol_grams = drink.abv * drink.volume_ml * ETHANOL_DENSITY_G_PER_ML / 100
            total_alcohol_grams += alcohol_grams

        # Calculate BAC from total alcohol consumed (Widmark formula uses grams)
        weight_grams = guest.weight * LBS_TO_KG_CONVERSION * 1000
        bac = (total_alcohol_grams / (weight_grams * AVERAGE_GENDER_CONSTANT)) * 100

        # Find the earliest consumption time before this timestamp
        earliest_consumption = min(relevant_consumptions, key=lambda c: c.timestamp)
        total_hours_elapsed = (timestamp - earliest_consumption.timestamp).total_seconds() / 3600

        # Apply metabolism: BAC decreases at a relatively constant rate (~0.015% per hour)
        metabolized_bac = BAC_METABOLISM_RATE * total_hours_elapsed
        bac = max(0, bac - metabolized_bac)

        bac_values.append(round(min(bac, BAC_DISPLAY_CAP), BAC_DECIMAL_PRECISION))
    
    # Create Plotly figure
    fig = go.Figure()
    
    from app import format_local_time

    # Add BAC line
    fig.add_trace(go.Scatter(
        x=[format_local_time(t, '%H:%M') for t in timestamps],
        y=bac_values,
        mode='lines+markers',
        name='BAC %',
        line=dict(color='rgba(220, 57, 18, 0.8)', width=3)
    ))
    
    # Add markers for drink consumptions
    drink_times = []
    drink_names = []
    drink_y = []  # Y-position based on when the drink was consumed
    
    for consumption in guest.drinks:
        if consumption.timestamp >= start_time:
            drink_times.append(format_local_time(consumption.timestamp, '%H:%M'))
            drink_names.append(f"{consumption.drink.name} ({consumption.drink.abv}%)")
            
            # Find the closest timestamp index
            closest_idx = min(range(len(timestamps)), 
                             key=lambda i: abs((timestamps[i] - consumption.timestamp).total_seconds()))
            drink_y.append(bac_values[closest_idx])
    
    fig.add_trace(go.Scatter(
        x=drink_times,
        y=drink_y,
        mode='markers',
        marker=dict(size=10, symbol='diamond', color='rgba(33, 150, 243, 0.8)'),
        name='Drinks',
        text=drink_names,
        hoverinfo='text+x+y'
    ))
    
    # Add horizontal lines for reference BAC levels
    fig.add_shape(
        type="line", line=dict(dash="dash", color="rgba(255, 153, 51, 0.8)", width=2),
        x0=format_local_time(timestamps[0], '%H:%M'), y0=BAC_LEGAL_LIMIT,
        x1=format_local_time(timestamps[-1], '%H:%M'), y1=0.08
    )
    
    fig.add_annotation(
        x=format_local_time(timestamps[0], '%H:%M'), y=0.08,
        text=f"{BAC_LEGAL_LIMIT}% - Legal Limit",
        showarrow=False,
        xshift=50,
        font=dict(color="rgba(255, 153, 51, 0.8)")
    )
    
    # Update layout
    fig.update_layout(
        title=f"BAC Timeline for {guest.name}",
        xaxis_title="Time",
        yaxis_title="Blood Alcohol Content (%)",
        hovermode="closest",
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    # Convert to JSON for rendering in template
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(graphJSON)

@host_bp.route('/group_bac_chart', methods=['GET'])
def group_bac_chart():
    """
    Generate BAC chart data for all guests with valid data.
    
    This endpoint creates a Plotly chart showing the estimated BAC over time for
    all guests who have weight information and have consumed drinks. The chart
    displays multiple lines, one for each guest, showing BAC levels over the
    past 6 hours at 15-minute intervals.
    
    Returns:
        JSON: Plotly chart configuration as JSON string, or empty chart if no valid guests.
    """
    guests = Guest.query.all()
    
    # Only include guests with weight and drinks
    valid_guests = [g for g in guests if g.weight and g.weight > 0 and g.drinks]
    
    # Generate BAC timeline
    now = datetime.utcnow()
    start_time = now - timedelta(hours=6)  # Show 6 hours of history
    
    # Create timestamps at 15-minute intervals
    timestamps = []
    current = start_time
    while current <= now:
        timestamps.append(current)
        current += timedelta(minutes=15)
    
    # Create Plotly figure
    fig = go.Figure()
    
    # If no valid guests, create an empty chart with a message
    if not valid_guests:
        # Create timestamps for empty chart
        timestamps_str = [format_local_time(t, '%H:%M') for t in timestamps]
        
        # Add empty line for visual reference
        fig.add_trace(go.Scatter(
            x=timestamps_str,
            y=[0] * len(timestamps),
            mode='lines',
            name='No data',
            line=dict(color='rgba(200, 200, 200, 0.5)', dash='dash')
        ))
        
        # Add annotation explaining the empty chart
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            text="No drink data available yet.<br>Add drinks for guests with weight information to see BAC charts.",
            showarrow=False,
            font=dict(size=14)
        )
    else:
        # Add BAC line for each guest
        for guest in valid_guests:
            # Calculate BAC at each timestamp
            bac_values = []
            
            for timestamp in timestamps:
                # Filter consumptions before this timestamp
                relevant_consumptions = [c for c in guest.drinks if c.timestamp <= timestamp]
                
                # Calculate BAC at this timestamp
                if not relevant_consumptions:
                    bac_values.append(0)
                    continue
                
                # Calculate total alcohol consumed before this timestamp
                total_alcohol_grams = 0

                for consumption in relevant_consumptions:
                    drink = consumption.drink
                    # Calculate alcohol in grams: ABV * volume(ml) * density of ethanol in g/ml / 100
                    alcohol_grams = drink.abv * drink.volume_ml * ETHANOL_DENSITY_G_PER_ML / 100
                    total_alcohol_grams += alcohol_grams

                # Calculate BAC from total alcohol consumed (Widmark formula uses grams)
                weight_grams = guest.weight * LBS_TO_KG_CONVERSION * 1000
                bac = (total_alcohol_grams / (weight_grams * AVERAGE_GENDER_CONSTANT)) * 100

                # Find the earliest consumption time before this timestamp
                earliest_consumption = min(relevant_consumptions, key=lambda c: c.timestamp)
                total_hours_elapsed = (timestamp - earliest_consumption.timestamp).total_seconds() / 3600

                # Apply metabolism: BAC decreases at a relatively constant rate (~0.015% per hour)
                metabolized_bac = BAC_METABOLISM_RATE * total_hours_elapsed
                bac = max(0, bac - metabolized_bac)

                bac_values.append(round(min(bac, BAC_DISPLAY_CAP), BAC_DECIMAL_PRECISION))
            
            # Add line for this guest
            fig.add_trace(go.Scatter(
                x=[format_local_time(t, '%H:%M') for t in timestamps],
                y=bac_values,
                mode='lines',
                name=guest.name,
                hoverinfo='x+y+name'
            ))
    
    # Add horizontal line for reference BAC level
    fig.add_shape(
        type="line", line=dict(dash="dash", color="rgba(255, 153, 51, 0.8)", width=2),
        x0=format_local_time(timestamps[0], '%H:%M'), y0=BAC_LEGAL_LIMIT, 
        x1=format_local_time(timestamps[-1], '%H:%M'), y1=0.08
    )
    
    fig.add_annotation(
        x=format_local_time(timestamps[0], '%H:%M'), y=0.08,
        text=f"{BAC_LEGAL_LIMIT}% - Legal Limit",
        showarrow=False,
        xshift=50,
        font=dict(color="rgba(255, 153, 51, 0.8)")
    )
    
    # Update layout
    fig.update_layout(
        title="Group BAC Timeline",
        xaxis_title="Time",
        yaxis_title="Blood Alcohol Content (%)",
        hovermode="closest",
        height=600,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    # Convert to JSON for rendering in template
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(graphJSON)
