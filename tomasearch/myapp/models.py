# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
        
class Functions(models.Model):
    """Model generated from table 'genes_and_go_terms'"""
    
    id = models.IntegerField(blank=True, null=False, primary_key=True, db_column="id")
    gene = models.CharField(max_length=100, blank=True, null=False, db_column = "gene")
    go_identifier = models.CharField(max_length=100, blank=True, null=True, db_column = "go_identifier")
    go_term = models.CharField(max_length=300, blank=True, null=True, db_column="go_term")
    subontology = models.CharField(max_length=100, blank=True, null=True, db_column="subontology")
    
    class Meta:
        db_table = "genes_and_go_terms"
        
class Subgraph(models.Model):
    """Model generated from table 'genes_and_subgraph'"""
    
    id = models.IntegerField(blank=True, null=False, primary_key=True, db_column="id")
    gene = models.CharField(max_length=50, blank=False, null=False, db_column = "gene")
    subgraph = models.IntegerField(blank=True, null=False, db_column = "subgraph")
    
    class Meta:
        db_table = "genes_and_subgraph"
        
class Enrichment(models.Model):
    """Model generated from table 'go_terms_and_enrichment'"""
    
    id = models.IntegerField(blank=True, null=False, primary_key=True, db_column="id")
    go_identifier = models.CharField(max_length=100, blank=True, null=False, db_column = "go_identifier")
    subgraph = models.IntegerField(blank=True, null=False, db_column = "subgraph")
    enrichment = models.FloatField(blank=True, null=False, db_column = "enrichment")
    p_value = models.FloatField(blank=True, null=False, db_column = "p_value")
    
    class Meta:
        db_table = "go_terms_and_enrichment"