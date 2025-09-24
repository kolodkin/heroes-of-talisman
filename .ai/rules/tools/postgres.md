---
description: postgres mcp guidelines

globs:
alwaysApply: true
---

# PostgreSQL MCP

## Purpose

Database schema design, query optimization, and backend development assistance.

## Key Tools

- `list_schemas/objects` - Explore database structure
- `get_object_details` - Detailed table/view information
- `execute_sql` - Run read-only queries
- `explain_query` - Analyze query performance
- `analyze_query_indexes` - Index optimization recommendations
- `get_top_queries` - Find slow/resource-intensive queries
- `analyze_db_health` - Database health checks

## When to Use

✅ Schema design, API queries, performance optimization, debugging, migrations
❌ Production modifications, direct deployments without review

## Common Workflows

1. **Schema Design**: Design tables → Generate migrations → Validate constraints
2. **Query Optimization**: Profile slow queries → Analyze execution plans → Suggest indexes
3. **API Development**: Design queries → Optimize for endpoints → Test performance

## Best Practices

- Use read-only connections for exploration
- Always explain queries before production
- Test with realistic data volumes
- Design proper indexes for query patterns
- Validate migrations thoroughly
