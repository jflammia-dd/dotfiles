# Event Processing Pipeline

## Introduction

This document explains how the event processing pipeline works. The pipeline transforms raw events from producers into processed records that consumers can query. It is used by the analytics team and the reporting system.

## Core Concepts

**Events** are raw records emitted by services. Each event has a timestamp, a type and a payload. Events are immutable once written.

**Processors** are stateless workers that transform events. They read from input queues, apply transformations and write to output queues.

**Sinks** are the final destinations for processed events. A sink can be a database, a search index or another message queue.

## How the Pipeline Works

### Stage 1: Ingestion

Producers write events to the ingestion layer via the Events API. The API validates the event schema and assigns a unique event ID. Events that fail validation are written to a dead-letter queue for inspection.

The ingestion layer batches events for efficiency. By default it holds up to 1000 events or waits 500ms, whichever comes first, before flushing to the processing queue.

### Stage 2: Processing

Processors consume events from the processing queue. Each processor is responsible for one type of transformation: enrichment, filtering, aggregation or routing. Processors can be chained: the output of one processor becomes the input of the next.

Enrichment processors add metadata to events using reference data. For example, a geographic enrichment processor adds country and city information to events that carry an IP address.

Filtering processors drop events that don't match a set of conditions. Conditions are expressed as simple key-value predicates or as more complex expressions using the pipeline's filter DSL.

Aggregation processors combine multiple events into a summary event. They operate over a configurable time window, typically 1 minute or 5 minutes.

### Stage 3: Delivery

Processed events are delivered to sinks. The delivery layer handles retries: if a sink is unavailable, delivery is retried with exponential backoff, up to a configurable maximum number of attempts. After all retries are exhausted, the event is written to a dead-letter queue.

Sinks can be registered dynamically. Adding a new sink requires no changes to the pipeline configuration — the delivery layer discovers sinks via a registry that it polls every 30 seconds.

### Stage 4: Monitoring

The pipeline emits metrics at each stage. Ingestion rate, processing latency, delivery success rate and dead-letter queue depth are all tracked. Alerts fire when dead-letter queue depth exceeds 1000 events or when delivery success rate drops below 99%.

## Common Issues

**High dead-letter queue depth** usually means either the sink is unavailable or events are failing schema validation. Check the sink's health endpoint and inspect the dead-letter queue for representative failures.

**High processing latency** usually means one processor in the chain is slow. Check the per-processor latency metrics to identify the bottleneck.

**Events appearing out of order** can happen when multiple processors run in parallel. The pipeline does not guarantee ordering across parallel processors. If ordering matters, configure the routing processor to send all events of a given type to a single processor instance.
