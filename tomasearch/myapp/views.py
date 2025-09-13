# Create your views here.
import csv
import json
from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse
from .models import *
from django.db.models.functions import Lower
import networkx as nx
from .graph_loader import *
from django.core.serializers.json import DjangoJSONEncoder

def home_page(request):
    """ Home page. """
    return render(request, "myapp/home.html")

def how_it_works_page(request):
    """ How it works page. """
    return render(request, "myapp/how_it_works.html")

def information_page(request):
    """ Information page. """
    return render(request, "myapp/information.html")

def search(request):
    """ Search page. """
    return render(request, "myapp/search.html")

def search_gene(request):
    """ Search by genes. """
    results = []
    columns = []
    
    if request.method == "POST":
        # Dict with relationship between checkbox and columns
        checkbox_columns = {
            "1": "go_identifier",
            "2": "go_term",
            "3": "subontology",
        }
        
        # Get the selected checkbox
        selected_options = request.POST.getlist("options")
        # Check if the fourth checkbox is selected (T or F)
        only_subgraph = set(selected_options) == {"4"}
        include_subgraph = "4" in selected_options
        
        # Get the column names
        selected_fields = [checkbox_columns[opt] for opt in selected_options if opt in checkbox_columns]
        # Get the genes
        text = request.POST.get("inputText", "")
        genes = [g.strip().lower() for g in text.split(",") if g.strip()]
        
        # If we only have the checkbox number 4, we only display the information from Subgraph table
        if only_subgraph:
            results = Subgraph.objects.filter(
                gene__in=genes
            ).values('id', 'gene', 'subgraph')
            columns = ['id', 'gene', 'subgraph']
        elif include_subgraph:
            # If we have more than the fourth checkbox, we need to display the information from the both tables
            func_results = Functions.objects.annotate(
                gene_lower=Lower("gene")
            ).filter(gene_lower__in=genes).values("gene", *selected_fields)
            
            subgraphs = Subgraph.objects.filter(
                gene__in=[row["gene"] for row in func_results]
            ).values("gene", "subgraph")

            # Dict with gene and subgraph
            subgraph_map = {s["gene"]: s["subgraph"] for s in subgraphs}
            
            # Add the subgraph
            for row in func_results:
                row["subgraph"] = subgraph_map.get(row["gene"], "")
            
            # Add the the enrichment and p_value to each gene if the GO identifier is selected
            if "1" in selected_options:
                go_identifiers = [row.get("go_identifier") for row in func_results if row.get("go_identifier")]
                subgraph_names = [row.get("subgraph") for row in func_results if row.get("subgraph")]

                enrich_pvalue = Enrichment.objects.filter(
                    go_identifier__in=go_identifiers,
                    subgraph__in=subgraph_names
                ).values("go_identifier", "enrichment", "p_value")

                enrich_map = {g["go_identifier"]: g["enrichment"] for g in enrich_pvalue}
                pvalue_map = {g["go_identifier"]: g["p_value"] for g in enrich_pvalue}

                for row in func_results:
                    row["enrichment"] = enrich_map.get(row.get("go_identifier"), "")
                    row["p_value"] = pvalue_map.get(row.get("go_identifier"), "")
            else:
                for row in func_results:
                    row["enrichment"] = ""
                    row["p_value"] = ""

            results = func_results
            columns = ["gene"] + selected_fields + ["subgraph", "enrichment", "p_value"]
        else:
            results = Functions.objects.annotate(
                gene_lower=Lower("gene")
            ).filter(gene_lower__in=genes).values("gene", *selected_fields)
            columns = ["gene"] + selected_fields
            
        request.session["csv_results"] = list(results)
        request.session["csv_columns"] = columns

        return render(request, "myapp/search_results.html", {
            "results": results,
            "columns": columns,
        })
        
    return render(request, "myapp/search.html")

def search_go_identifier(request):
    """ Search by GO identifiers. """
    results = []
    columns = []
    
    if request.method == "POST":
        # Dict with relationship between checkbox and columns
        checkbox_columns = {
            "1": "go_term",
            "2": "subontology",
        }
        
        # Get the selected checkbox
        selected_options = request.POST.getlist("options")
        # Get T or F if 3 is selected or not
        include_subgraph = "3" in selected_options
        
        # Get the column names
        selected_fields = [checkbox_columns[opt] for opt in selected_options if opt in checkbox_columns]
        # Get the go identifiers
        text = request.POST.get("inputText", "")
        ident = [g.strip().lower() for g in text.split(",") if g.strip()]
        
        func_results = Functions.objects.annotate(
            go_identifiers_lower=Lower("go_identifier")
        ).filter(go_identifiers_lower__in=ident).values("gene", "go_identifier", *selected_fields)
        
        results = func_results

        if include_subgraph:
            subgraphs = Subgraph.objects.filter(
                gene__in=[row["gene"] for row in func_results]
            ).values("gene", "subgraph")

            # Dict with gene and subgraph
            subgraph_map = {s["gene"]: s["subgraph"] for s in subgraphs}

            # Add the subgraph to each gene
            for row in func_results:
                row["subgraph"] = subgraph_map.get(row["gene"], "")
                
            go_identifiers = [row.get("go_identifier") for row in func_results if row.get("go_identifier")]
            subgraph_names = [row.get("subgraph") for row in func_results if row.get("subgraph")]

            enrich_pvalue = Enrichment.objects.filter(
                go_identifier__in=go_identifiers,
                subgraph__in=subgraph_names
            ).values("go_identifier", "subgraph", "enrichment", "p_value")

            enrich_map = {(g["go_identifier"], g["subgraph"]): g["enrichment"] for g in enrich_pvalue}
            pvalue_map = {(g["go_identifier"], g["subgraph"]): g["p_value"] for g in enrich_pvalue}

            for row in func_results:
                key = (row.get("go_identifier"), row.get("subgraph"))
                row["enrichment"] = enrich_map.get(key, "")
                row["p_value"] = pvalue_map.get(key, "")

            columns = ["gene", "go_identifier"] + selected_fields + ["subgraph", "enrichment", "p_value"]
        else:
            columns = ["gene", "go_identifier"] + selected_fields          
            
        request.session["csv_results"] = list(results)
        request.session["csv_columns"] = columns

        return render(request, "myapp/search_results.html", {
            "results": results,
            "columns": columns,
        })
        
    return render(request, "myapp/search.html")

def search_go_term(request):
    """ Search by GO terms."""
    results = []
    columns = []
    
    if request.method == "POST":
        # Dict with relationship between checkbox and columns
        checkbox_columns = {
            "1": "go_identifier",
            "2": "subontology",
        }
        
        # Get the selected checkbox
        selected_options = request.POST.getlist("options")
        include_subgraph = "3" in selected_options
        # Get the column names
        selected_fields = [checkbox_columns[opt] for opt in selected_options if opt in checkbox_columns]

        # User input
        text = request.POST.get("inputText", "")
        go_terms = [g.strip().lower() for g in text.split(",") if g.strip()]
        
        # Dynamic query construction
        query = Q()
        for term in go_terms:
            query |= Q(go_term_lower__contains=term)

        func_results = Functions.objects.annotate(
            go_term_lower=Lower("go_term")
        ).filter(query).values("gene", "go_term", *selected_fields)
        
        results = func_results

        if include_subgraph:
            subgraphs = Subgraph.objects.filter(
                gene__in=[row["gene"] for row in func_results]
            ).values("gene", "subgraph")

            subgraph_map = {s["gene"]: s["subgraph"] for s in subgraphs}

            for row in func_results:
                row["subgraph"] = subgraph_map.get(row["gene"], "")
                
            # Add the the enrichment and p_value to each gene
            if "1" in selected_options:
                go_identifiers = [row.get("go_identifier") for row in func_results if row.get("go_identifier")]
                subgraph_names = [row.get("subgraph") for row in func_results if row.get("subgraph")]

                enrich_pvalue = Enrichment.objects.filter(
                    go_identifier__in=go_identifiers,
                    subgraph__in=subgraph_names
                ).values("go_identifier", "enrichment", "p_value")

                enrich_map = {g["go_identifier"]: g["enrichment"] for g in enrich_pvalue}
                pvalue_map = {g["go_identifier"]: g["p_value"] for g in enrich_pvalue}

                for row in func_results:
                    row["enrichment"] = enrich_map.get(row.get("go_identifier"), "")
                    row["p_value"] = pvalue_map.get(row.get("go_identifier"), "")
            else:
                for row in func_results:
                    row["enrichment"] = ""
                    row["p_value"] = ""

            results = func_results
            columns = ["gene", "go_term"] + selected_fields + ["subgraph", "enrichment", "p_value"]

        else:
            columns = ["gene", "go_term"] + selected_fields

        request.session["csv_results"] = list(results)
        request.session["csv_columns"] = columns

        return render(request, "myapp/search_results.html", {
            "results": results,
            "columns": columns,
        })

    return render(request, "myapp/search.html")

def search_subontology(request):
    """ Search genes by subontology. """
    
    results = []
    columns = []
    
    if request.method == "POST":
        # Dict with relationship between checkbox and columns
        checkbox_columns = {
            "1": "go_identifier",
            "2": "go_term",
        }
        
        checkbox_subontologies = {
            "1": "Cellular component",
            "2": "Biological process",
            "3": "Molecular function",
        }
        
        # Get the selected checkbox (subontologies and options)
        selected_subontology = request.POST.getlist("options_subontology")
        selected_options = request.POST.getlist("options")

        # Get T or F if 3 is selected or not
        include_subgraph = "3" in selected_options
        
        # Get the column names
        selected_fields = [checkbox_columns[opt] for opt in selected_options if opt in checkbox_columns]

        # Get the subontology names
        subontologies = [checkbox_subontologies[asp.lower()].lower() for asp in selected_subontology if asp.lower() in checkbox_subontologies]
        subontologies_results = Functions.objects.filter(subontology__in=subontologies).values("gene", "subontology", *selected_fields)

        results = subontologies_results

        if include_subgraph:
            subgraphs = Subgraph.objects.filter(
                gene__in=[row["gene"] for row in subontologies_results]
            ).values("gene", "subgraph")

            # Dict with gene and subgraph
            subgraph_map = {s["gene"]: s["subgraph"] for s in subgraphs}

            # Add the subgraph to each gene
            for row in subontologies_results:
                row["subgraph"] = subgraph_map.get(row["gene"], "")
            
            # If the user requests the GO identifier and subgraph, we need to get the enrichment and p_value
            if "1" in selected_options:
                # Get the genes from the subontologies results
                genes = [row["gene"] for row in subontologies_results if row.get("gene")]
                # Get the GO identifiers from the Functions table
                go_identifiers = Functions.objects.filter(gene__in=genes).values_list("go_identifier", flat=True)
                subgraph_names = [row.get("subgraph") for row in subontologies_results if row.get("subgraph")]
                # Get the enrichment and p_value from the Enrichment table
                enrich_pvalue = Enrichment.objects.filter(
                    go_identifier__in=go_identifiers,
                    subgraph__in=subgraph_names
                ).values("go_identifier", "enrichment", "p_value")
                
                # Create maps for enrichment and p_value
                enrich_map = {g["go_identifier"]: g["enrichment"] for g in enrich_pvalue}
                pvalue_map = {g["go_identifier"]: g["p_value"] for g in enrich_pvalue} 
                 
                # Add enrichment and p_value to each row in the results
                for row in subontologies_results:
                    row["enrichment"] = enrich_map.get(row.get("go_identifier"), "")
                    row["p_value"] = pvalue_map.get(row.get("go_identifier"), "")  
                    
                # Set the columns for the results
                columns = ["gene", "subontology"] + selected_fields + ["subgraph", "enrichment", "p_value"]
            else:
                # If the user does not request the GO identifier and subgraph, we don't need to get the enrichment and p_value
                columns = ["gene", "subontology"] + selected_fields + ["subgraph"]  

        else:
            # If the user does not request the subgraph, we don't need to get the subgraph and enrichment/p_value
            columns = ["gene", "subontology"] + selected_fields          
            
        request.session["csv_results"] = list(results)
        request.session["csv_columns"] = columns

        return render(request, "myapp/search_results.html", {
            "results": results,
            "columns": columns,
        })
        
    return render(request, "myapp/search_subontologies.html")

def graph_to_vis_json(G):
    """ Convert a NetworkX graph to Vis.js JSON format. """
    # Convert a NetworkX graph to Vis.js JSON format
    if G is None:
        return {"nodes": [], "edges": []}
    
    if not isinstance(G, nx.Graph):
        raise ValueError("Input must be a NetworkX graph (Graph or DiGraph).")
    
    nodes = []
    edges = []
    
    # Use a layout algorithm to position the nodes
    pos = nx.spring_layout(G, iterations=50, seed=42)
    
    # Scale positions to fit within a defined canvas size
    min_x = min(p[0] for p in pos.values())
    max_x = max(p[0] for p in pos.values())
    min_y = min(p[1] for p in pos.values())
    max_y = max(p[1] for p in pos.values())
    
    # Define canvas size and padding
    canvas_width = 800
    canvas_height = 600
    padding = 50
    
    # Scale positions to fit within the canvas
    scale_x = (canvas_width - 2 * padding) / (max_x - min_x) if (max_x - min_x) != 0 else 1
    scale_y = (canvas_height - 2 * padding) / (max_y - min_y) if (max_y - min_y) != 0 else 1
    
    # Create nodes and edges in Vis.js format
    for n in G.nodes():
        x_scaled = (pos[n][0] - min_x) * scale_x + padding
        y_scaled = (pos[n][1] - min_y) * scale_y + padding
        nodes.append({
            "id": str(n),
            "label": str(n),
            "x": x_scaled,
            "y": y_scaled,
            "fixed": True
        })

    for u, v in G.edges():
        edges.append({"from": str(u), "to": str(v)})

    return {"nodes": nodes, "edges": edges}


def images_page(request):
    """ Images page with graph visualization. """
    if request.method == "POST":
        global G, SUBGRAPHS
        
        # Check if the graph is loaded
        if G is None or SUBGRAPHS is None:
            return HttpResponse("Graph not loaded. Please try again later.", content_type="text/plain")
        # Get user input
        text = request.POST.get("inputText", "").strip()
        
        if isinstance(G, nx.DiGraph):
            G = G.to_undirected()
        # Get connected components and subgraphs
        components = list(nx.connected_components(G))
        subgraphs = [G.subgraph(c).copy() for c in components]

        sg = None
        sg_index = None

        if text.isdigit():
            # Search by subgraph index
            index = int(text) - 1
            if 0 <= index < len(SUBGRAPHS):
                sg = SUBGRAPHS[index]
                sg_index = index + 1
                print(f"Subgraph index: {sg_index}")
            else:
                return HttpResponse(f"No subgraph with index {index + 1}.", content_type="text/plain")
        else:
            # Search by gene names
            genes = [g.strip().lower() for g in text.split(",") if g.strip()]
            for i, sub in enumerate(subgraphs):
                sub_nodes_lower = set(map(str.lower, sub.nodes))
                print(sub_nodes_lower)
                if any(g in sub_nodes_lower for g in genes):
                    sg = sub
                    sg_index = i + 1
                    break
            if sg is None:
                return HttpResponse("No subgraphs found for the provided genes.", content_type="text/plain")

        # Convert subgraph to Vis.js format
        vis_data = graph_to_vis_json(sg)
        subgraph_genes = list(sg.nodes)

        # Get the gene information
        go_terms_qs = Functions.objects.filter(gene__in=subgraph_genes)
        go_terms_data = []
        go_identifiers = set()
        
        for f in go_terms_qs:
            go_terms_data.append({
                "gene": f.gene,
                "go_identifier": f.go_identifier,
                "go_term": f.go_term,
                "subontology": f.subontology,
            })
            if f.go_identifier:
                ident = [i.strip() for i in f.go_identifier.replace(";", ",").replace("|", ",").split(",")]
                go_identifiers.update(ident)
        
        # Get enrichment information
        enrichment_qs = Enrichment.objects.filter(go_identifier__in=go_identifiers, subgraph=sg_index)
        enrichment_data = []
        for e in enrichment_qs:
            enrichment_data.append({
                "go_identifier": e.go_identifier,
                "subgraph": e.subgraph,
                "enrichment": e.enrichment,
                "p_value": e.p_value,
            })
        # Subgraph data
        subgraph_qs = Subgraph.objects.filter(subgraph=sg_index)
        subgraph_data = []
        for s in subgraph_qs:
            subgraph_data.append({
                "gene": s.gene,
                "subgraph": s.subgraph,
            })

        context = {
            'vis_data': json.dumps(vis_data, cls=DjangoJSONEncoder),
            'go_terms_data': json.dumps(go_terms_data, cls=DjangoJSONEncoder),
            'enrichment_data': json.dumps(enrichment_data, cls=DjangoJSONEncoder),
            'subgraph_data': json.dumps(subgraph_data, cls=DjangoJSONEncoder),
            'genes': text,
        }
        return render(request, "myapp/images.html", context)

    return render(request, "myapp/images.html", {})

def download_csv(request):
    """ Download search results as CSV. """
    results = request.session.get("csv_results", [])
    columns = request.session.get("csv_columns", [])
    
    if not results or not columns:
        return HttpResponse("No data to export.", content_type="text/plain")
    
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="results.csv"'
    
    writer = csv.writer(response)
    writer.writerow(columns)
    
    for row in results:
        writer.writerow([row.get(col, "") for col in columns])

    return response