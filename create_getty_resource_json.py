#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" create json for indexing """
from __future__ import unicode_literals
import sys
import argparse
import itertools
import rdflib
import os
from rdflib import ConjunctiveGraph, Namespace, Graph
from rdflib.resource import Resource
from rdflib.namespace import RDF
from pyld import jsonld
import json

GVP = Namespace('http://vocab.getty.edu/ontology#')

def main(argv=None):
    parser = argparse.ArgumentParser()

    if argv is None:
        argv = parser.parse_args()

    graph = ConjunctiveGraph('Sleepycat')
    graph.open("store-bu2", create=False)

    # there must be a beter way?? I want to iterate over all subjects...
    for subject, statements in itertools.groupby(graph, lambda g: g[0]):
        resource = Resource(graph, subject)
        # okay, so we only want to index certain types of records,
        # where this is true for the type:
        # rdfs:subClassOf = gvp:Subject, skos:Concept
        # Should be some way
        # to check but damned if I can figure it out
        types_we_want = [
            GVP.AdminPlaceContent,
            GVP.Concept,
            GVP.GroupConcept,
            GVP.PersonConcept,
            GVP.PhysAdminPlaceConcept,
            GVP.PhysPlaceConcept,
            GVP.UnknownPersonConcept,
        ]
        if (resource.value(RDF.type) is None):
            pass
        elif not(resource.value(RDF.type).identifier in types_we_want):
            pass
        else:

            text_we_want = [
                'http://vocab.getty.edu/ontology#prefLabelGVP',
                'http://www.w3.org/2008/05/skos-xl#prefLabel',
                'http://www.w3.org/2008/05/skos-xl#altLabel',
            ]

            values_we_want = [
                'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
            ] + text_we_want

            # create a sub graph, just for the current resource/subject
            sub_graph = Graph()
            # loop over all statements about subject
            for s, p, o in statements:
                predicate = p.decode()
                if predicate in values_we_want:  # the stuff we want
                    sub_graph.add((s, p, o))
                    # we want the full text from these
                    if predicate in text_we_want:
                        for inner_p, inner_o in graph.predicate_objects(subject=o):
                            if (
                                # type and part of speech look interesting
                                inner_p in [GVP.termType, GVP.termPOS] or
                                # any literal values
                                type(inner_o) == rdflib.term.Literal
                            ):
                                sub_graph.add((o, inner_p, inner_o))
            # re-frame the json per template frame
            c = json.loads(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                             'dist/context.json')).read())
            framed = jsonld.frame(
                json.loads(sub_graph.serialize(format='json-ld')),
                {
                    "@context": c,
                    "@type": "http://vocab.getty.edu/ontology#Concept"
                },
            )
            # force the context compaction with embeded context
            compacted = jsonld.compact(framed, c)
            # put back context reference for index artifact
            compacted['@context'] = 'http://tingletech.github.io/vocab_search/context.json'
            sub_graph.close()
            sub_graph = None
            outfile = os.path.join('out', '{0}.json'.format(s.md5_term_hash()))
            with open(outfile, 'w') as f:
                json.dump(compacted, f, sort_keys=True, indent=2)
    graph.close()


# main() idiom for importing into REPL for debugging
if __name__ == "__main__":
    sys.exit(main())


"""
Copyright © 2016, Regents of the University of California
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
- Neither the name of the University of California nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
