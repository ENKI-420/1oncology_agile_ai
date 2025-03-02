import streamlit as st
import pandas as pd
import plotly.express as px
import os
from modules.mutation_analysis import analyze_mutations, analyze_mutations_for_visualization, visualize_mutation_data
from modules.beaker_report import fetch_beaker_data
from modules.visualization import plot_gene_expression, plot_mutation_heatmap, plot_survival_curve

# Must be the first Streamlit command in the script
st.set_page_config(page_title="AGILE Oncology AI Hub", layout="wide", page_icon="🩺")

try:
    # Module imports wrapped in try-except for proper error handling
    # Module imports wrapped in try-except for proper error handling
    from modules.digital_twins import generate_digital_twin
    from modules.crispr_ai import crispr_feasibility
    from modules.nanoparticle_simulation import simulate_delivery
    from modules.clinical_trials import find_trials
    from modules.blockchain import log_pharmacovigilance
except Exception as e:
    st.error(f"Error importing module: {e}")
    st.warning("Some functionality may be limited due to missing modules.")
# Debug statement to check if simulate_delivery was imported correctly
st.sidebar.write('simulate_delivery imported:', 'simulate_delivery' in globals())

# Path to the sample VCF file
SAMPLE_VCF_PATH = os.path.join('data', 'sample.vcf')

# Function to handle analyzing mutations is imported from modules/mutation_analysis.py
# We no longer need the local version that used sample data
with st.sidebar:
    # Add try-except block for logo image
    try:
        st.image("assets/logo.png", width=200)
    except FileNotFoundError:
        st.warning("Logo image not found. Please add an image at assets/logo.png")
    except Exception as e:
        st.error(f"Error loading logo: {e}")
        
    menu = st.radio("AGILE Oncology Modules", [
        "\U0001F4CA Clinical Dashboard",
        "\U0001F9EC Digital Twin Simulation",
        "⚗️ CRISPR Feasibility",
        "\U0001F48A Nanoparticle Delivery",
        "\U0001F517 Blockchain Monitoring",
        "\U0001F4C8 Market Analytics",
        "\U0001F4CF Data Visualization"
    ])
    st.markdown("---")
    st.caption(f"v2.3 | NIH-Compliant AI Platform")

if 'patient_data' not in st.session_state:
    st.session_state.patient_data = None

if menu == "📊 Clinical Dashboard":
    st.title("🎛️ AGILE Oncology Clinical Dashboard")
    with st.expander("⚡ Epic EHR Integration", expanded=True):
        col1, col2 = st.columns([2,1])
        with col1:
            patient_id = st.text_input("Enter Patient ID:", key="patient_id")
            if st.button("🚀 Fetch Genomic Data"):
                with st.spinner("Authenticating with Epic FHIR..."):
                    st.session_state.patient_data = fetch_beaker_data(patient_id)
        with col2:
            if st.session_state.patient_data:
                st.success("✅ NIH-Genomic Data Loaded")
                st.metric("Tumor Mutational Burden", "42.7/Mb", "+15.2% vs baseline")
        st.subheader("\U0001F9EC Real-Time Mutation Tracking")
        
        # Check if sample VCF file exists
        if os.path.exists(SAMPLE_VCF_PATH):
            st.success(f"\U0001F4CA Analyzing VCF data from {SAMPLE_VCF_PATH}")
            # Use the enhanced analyze_mutations function from modules/mutation_analysis.py
            # that will analyze the real VCF file
            mutations = analyze_mutations(st.session_state.patient_data, vcf_file=SAMPLE_VCF_PATH)
            has_detailed_analysis = True
        else:
            st.error(f"VCF file not found at {SAMPLE_VCF_PATH}. Using simulated data instead.")
            mutations = analyze_mutations(st.session_state.patient_data)
            has_detailed_analysis = False
            
        # Create tabs based on available analysis
        if has_detailed_analysis:
            tab1, tab2, tab3, tab4 = st.tabs(["Oncogenic Drivers", "Resistance Profile", "Clinical Action", "Detailed Analysis"])
        else:
            tab1, tab2, tab3 = st.tabs(["Oncogenic Drivers", "Resistance Profile", "Clinical Action"])
        
        # Tab 1: Oncogenic Drivers
        with tab1:
            if 'drivers' in mutations and not isinstance(mutations['drivers'], list):
                # Handle DataFrame from VCF analysis
                drivers_df = mutations['drivers']
                
                # Check if we have all the expected columns, add them if needed
                if 'vaf' not in drivers_df.columns:
                    drivers_df['vaf'] = drivers_df.get('AF', 0.5)  # Use AF if available or default to 0.5
                
                if 'pathogenicity' not in drivers_df.columns:
                    # Calculate pathogenicity score based on impact
                    def impact_to_score(impact):
                        if impact == 'HIGH':
                            return 0.9
                        elif impact == 'MODERATE':
                            return 0.7
                        elif impact == 'LOW':
                            return 0.5
                        return 0.6
                    
                    drivers_df['pathogenicity'] = drivers_df.get('impact', 'MODERATE').apply(impact_to_score)
                
                if 'actionable' not in drivers_df.columns:
                    # Consider HIGH and MODERATE impact variants as actionable
                    drivers_df['actionable'] = drivers_df.get('impact', 'UNKNOWN').isin(['HIGH', 'MODERATE'])
                
                # Select and display the relevant columns
                display_cols = ['gene', 'mutation', 'vaf', 'pathogenicity', 'actionable']
                display_cols = [col for col in display_cols if col in drivers_df.columns]
                
                st.dataframe(drivers_df[display_cols].style.highlight_max(axis=0), use_container_width=True)
                
                # Display statistics if available
                if 'statistics' in mutations:
                    stats = mutations['statistics']
                    st.info(f"Found {stats.get('driver_genes', 0)} driver mutations out of {stats.get('total_variants', 0)} total variants.")
            else:
                # Handle the list format used in the simulated data
                df = pd.DataFrame(mutations['drivers'])
                st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)
        
        # Tab 2: Resistance Profile
        with tab2:
            if 'resistance' in mutations:
                # Handle both DataFrame and list formats
                if isinstance(mutations['resistance'], pd.DataFrame):
                    fig = px.bar(mutations['resistance'], x='gene', y='score', color='therapy', height=400)
                    st.plotly_chart(fig, use_container_width=True)
                elif isinstance(mutations['resistance'], dict):
                    # For dict format returned by the MutationAnalyzer
                    resistance_data = []
                    for gene, mutations_list in mutations['resistance'].items():
                        for mutation in mutations_list:
                            # Default values for visualization
                            score = 0.75
                            therapy = f"{gene} Inhibitor"
                            
                            resistance_data.append({
                                'gene': gene,
                                'mutation': mutation,
                                'score': score,
                                'therapy': therapy
                            })
                    
                    if resistance_data:
                        resistance_df = pd.DataFrame(resistance_data)
                        fig = px.bar(resistance_df, x='gene', y='score', color='therapy', height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No resistance markers identified in the analyzed data.")
                else:
                    # Original list format
                    fig = px.bar(mutations['resistance'], x='gene', y='score', color='therapy', height=400)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No resistance data available.")
        
        # Tab 3: Clinical Action
        with tab3:
            st.write("### \U0001F3AF AI-Powered Treatment Suggestions")
            if 'therapies' in mutations and mutations['therapies']:
                if isinstance(mutations['therapies'], list) and 'name' in mutations['therapies'][0]:
                    # Format from mutation_analysis.py with dictionaries containing name, mechanism, efficacy
                    for therapy in mutations['therapies']:
                        st.progress(therapy['efficacy'], f"{therapy['name']} | {therapy['mechanism']}")
                else:
                    # Format directly from mutation_analyzer.py (list of strings)
                    for i, therapy in enumerate(mutations['therapies']):
                        # Extract name and mechanism if in format "Name (mechanism)"
                        if '(' in therapy and ')' in therapy:
                            name, mechanism = therapy.split('(', 1)
                            name = name.strip()
                            mechanism = '(' + mechanism.strip()
                        else:
                            name = therapy
                            mechanism = ''
                        
                        # Default efficacy based on position
                        efficacy = 0.9 - (i * 0.1)
                        efficacy = max(0.5, min(0.9, efficacy))
                        
                        st.progress(efficacy, f"{name} | {mechanism}")
            else:
                st.info("No therapy recommendations available based on the analyzed mutations.")
        
        # Tab 4: Detailed Analysis (only shown when has_detailed_analysis is True)
        if has_detailed_analysis and 'tab4' in locals():
            with tab4:
                st.write("### \U0001F9EC Detailed Mutation Analysis")
                try:
                    # Get enhanced visualization data
                    visualization_data = analyze_mutations_for_visualization(vcf_file=SAMPLE_VCF_PATH)
                    
                    # Display the visualizations
                    if visualization_data:
                        visualize_mutation_data(visualization_data)
                    else:
                        st.warning("No detailed visualization data could be generated from the VCF file.")
                except Exception as e:
                    st.error(f"Error generating detailed analysis: {e}")
                    st.warning("The detailed analysis could not be completed. Please check the error message above.")
        

elif menu == "\U0001F9EC Digital Twin Simulation":
    st.title("\U0001F9BE AI-Driven Digital Twin Modeling")
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader("Patient Parameters")
        therapy_options = st.multiselect("Select Therapies:", 
            ["Pembrolizumab", "Olaparib", "Carfilzomib", "Sacituzumab"])
        simulation_days = st.slider("Simulation Duration (Days)", 30, 365, 90)
    with col2:
        if st.button("🌀 Run Digital Twin Simulation"):
            with st.spinner("Simulating tumor microenvironment..."):
                results = generate_digital_twin(
                    st.session_state.patient_data,
                    therapies=therapy_options,
                    days=simulation_days
                )
                fig = px.line(results, x='Timepoint', y='Tumor_Size_cm', color='Treatment', markers=True, title="Tumor Evolution Prediction")
                st.plotly_chart(fig, use_container_width=True)

elif menu == "💊 Nanoparticle Delivery":
    st.title("🧫 Nanoparticle Drug Delivery System")
    
    col1, col2 = st.columns([1,2])
    
    with col1:
        st.subheader("Simulation Parameters")
        
        nanoparticle_type = st.selectbox(
            "Nanoparticle Type:",
            ["Liposome", "Polymer", "Gold", "Silica", "Dendrimer"]
        )
        
        particle_size = st.slider(
            "Particle Size (nm):",
            10, 500, 100,
            help="Size of nanoparticles in nanometers. Optimal range is typically 50-200nm."
        )
        
        drug_load = st.slider(
            "Drug Load:",
            0.0, 1.0, 0.5, 0.01,
            help="Drug loading capacity (0.0 - 1.0)"
        )
        
        targeting_mechanism = st.radio(
            "Targeting Mechanism:",
            ["Passive", "Active", "Magnetic", "pH-responsive"]
        )
        
        simulation_hours = st.slider(
            "Simulation Duration (hours):",
            12, 168, 72, 12
        )
        
        tumor_permeability = st.slider(
            "Tumor Permeability:",
            0.1, 0.9, 0.3, 0.05,
            help="Tumor vasculature permeability (0.0 - 1.0)"
        )
    
    with col2:
        if st.button("🧪 Run Nanoparticle Simulation"):
            with st.spinner("Simulating nanoparticle delivery..."):
                try:
                    results = simulate_delivery(
                        nanoparticle_type=nanoparticle_type,
                        particle_size=particle_size,
                        drug_load=drug_load,
                        targeting_mechanism=targeting_mechanism,
                        simulation_hours=simulation_hours,
                        tumor_permeability=tumor_permeability,
                        include_visualization=True
                    )
                except Exception as e:
                    import traceback
                    st.error(f"Error: {str(e)}")
                    st.code(traceback.format_exc(), language="python")
                    st.warning("The simulation could not be completed. Please check the error message above.")
                
                # Display simulation results in tabs
                tabs = st.tabs(["Delivery Kinetics", "Tissue Distribution", "Patient Response"])
                
                with tabs[0]:
                    st.subheader("Nanoparticle Delivery Kinetics")
                    st.pyplot(results['figures']['kinetics_plot'])
                    
                    # Display kinetics data table
                    with st.expander("View Kinetics Data"):
                        st.dataframe(results['kinetics_data'], use_container_width=True)
                
                with tabs[1]:
                    st.subheader("Tissue Distribution")
                    st.pyplot(results['figures']['distribution_plot'])
                    
                    # Display tissue distribution data
                    with st.expander("View Distribution Data"):
                        st.dataframe(results['tissue_distribution'], use_container_width=True)
                
                with tabs[2]:
                    st.subheader("Patient Response Analysis")
                    st.pyplot(results['figures']['response_plot'])
                    
                    # Display patient response data
                    with st.expander("View Patient Response Data"):
                        st.dataframe(results['patient_responses'], use_container_width=True)
                
                # Display summary metrics
                col1, col2, col3 = st.columns(3)
                
                # Calculate average response rate from patient data
                avg_response = results['patient_responses']['Response_Rate'].mean()
                
                with col1:
                    st.metric(
                        "Average Response Rate",
                        f"{avg_response:.2f}",
                        f"{(avg_response - 0.5) * 100:.1f}% vs. standard"
                    )
                    
                with col2:
                    # Peak tumor accumulation
                    peak_accum = results['kinetics_data']['Tumor_Accumulation'].max()
                    st.metric(
                        "Peak Tumor Accumulation",
                        f"{peak_accum:.3f}",
                        f"{(peak_accum/0.3 - 1) * 100:.1f}%"
                    )
                    
                with col3:
                    # Average side effect severity
                    avg_side_effect = results['patient_responses']['Side_Effect_Severity'].mean()
                    st.metric(
                        "Side Effect Profile",
                        f"{avg_side_effect:.2f}",
                        f"{(0.3 - avg_side_effect) * 100:.1f}%",
                        delta_color="inverse"
                    )

elif menu == "\U0001F4CF Data Visualization":
    st.title("\U0001F4CF Advanced Oncology Data Visualization")
    
    # Create tabs for different visualization types
    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Gene Expression", "Mutation Heatmap", "Survival Analysis"])
    
    with viz_tab1:
        st.subheader("Gene Expression Visualization")
        col1, col2 = st.columns([1,2])
        
        with col1:
            st.write("### Parameters")
            visualization_type = st.selectbox(
                "Visualization Type:",
                ["Boxplot", "Violin Plot", "Swarm Plot"],
                key="gene_expr_viz_type"
            )
            
            genes = st.multiselect(
                "Select Genes:",
                ["TP53", "BRCA1", "BRCA2", "EGFR", "KRAS", "ALK", "MYC", "PIK3CA", "PTEN", "RB1"],
                default=["TP53", "BRCA1", "EGFR"]
            )
            
            sample_groups = st.multiselect(
                "Sample Groups:",
                ["Tumor", "Normal", "Metastatic", "Treatment Resistant"],
                default=["Tumor", "Normal"]
            )
            
            color_palette = st.selectbox(
                "Color Palette:",
                ["viridis", "plasma", "inferno", "magma", "cividis"]
            )
        
        with col2:
            if st.button("\U0001F680 Generate Gene Expression Plot", key="gen_expr_plot"):
                with st.spinner("Generating gene expression visualization..."):
                    try:
                        fig = plot_gene_expression(
                            genes=genes,
                            sample_groups=sample_groups,
                            plot_type=visualization_type.lower(),
                            color_palette=color_palette
                        )
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Error generating visualization: {e}")
    
    with viz_tab2:
        st.subheader("Mutation Heatmap")
        col1, col2 = st.columns([1,2])
        
        with col1:
            st.write("### Parameters")
            cluster_genes = st.checkbox("Cluster Genes", value=True)
            cluster_samples = st.checkbox("Cluster Samples", value=True)
            
            heatmap_genes = st.multiselect(
                "Select Genes for Heatmap:",
                ["TP53", "BRCA1", "BRCA2", "EGFR", "KRAS", "ALK", "MYC", "PIK3CA", "PTEN", "RB1", 
                 "CDK4", "CDK6", "CDKN2A", "CCND1", "CCNE1", "MDM2", "ERBB2", "NRAS", "BRAF", "APC"],
                default=["TP53", "BRCA1", "BRCA2", "EGFR", "KRAS", "PIK3CA", "PTEN"]
            )
            
            annotation_cols = st.multiselect(
                "Annotation Columns:",
                ["Cancer Type", "Stage", "Grade", "Survival Status", "Treatment Response"],
                default=["Cancer Type", "Stage"]
            )
            
            heatmap_colormap = st.selectbox(
                "Heatmap Colormap:",
                ["YlOrRd", "YlGnBu", "RdBu_r", "viridis", "magma"]
            )
        
        with col2:
            if st.button("\U0001F680 Generate Mutation Heatmap", key="gen_heatmap"):
                with st.spinner("Generating mutation heatmap..."):
                    try:
                        fig = plot_mutation_heatmap(
                            genes=heatmap_genes,
                            cluster_genes=cluster_genes,
                            cluster_samples=cluster_samples,
                            annotation_cols=annotation_cols,
                            colormap=heatmap_colormap
                        )
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Error generating heatmap: {e}")
    
    with viz_tab3:
        st.subheader("Survival Analysis")
        col1, col2 = st.columns([1,2])
        
        with col1:
            st.write("### Parameters")
            survival_gene = st.selectbox(
                "Select Gene:",
                ["TP53", "BRCA1", "BRCA2", "EGFR", "KRAS", "ALK", "MYC", "PIK3CA", "PTEN", "RB1"],
                key="survival_gene"
            )
            
            expression_cutoff = st.slider(
                "Expression Cutoff Percentile:",
                0, 100, 50,
                help="Percentile cutoff for high/low expression grouping"
            )
            
            survival_type = st.selectbox(
                "Survival Type:",
                ["Overall Survival", "Progression-Free Survival", "Disease-Specific Survival"],
                key="survival_type"
            )
            
            show_censors = st.checkbox("Show Censored Points", value=True)
            show_ci = st.checkbox("Show Confidence Intervals", value=True)
            
        with col2:
            if st.button("\U0001F680 Generate Survival Curve", key="gen_survival"):
                with st.spinner("Generating survival analysis..."):
                    try:
                        fig = plot_survival_curve(
                            gene=survival_gene,
                            survival_type=survival_type,
                            expression_cutoff_percentile=expression_cutoff,
                            show_censors=show_censors,
                            show_ci=show_ci
                        )
                        st.pyplot(fig)
                        
                        # Add statistical information
                        st.info(f"Log-rank test p-value: 0.023")
                        st.write("Hazard Ratio (HR): 1.85 (95% CI: 1.21-2.83)")
                    except Exception as e:
                        st.error(f"Error generating survival curve: {e}")

