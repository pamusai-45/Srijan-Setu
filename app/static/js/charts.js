// Chart.js Configurations with Brand Green Theme

const BRAND_PALETTE = [
    '#124C3A', // Forest Green
    '#63B99A', // Accent Mint
    '#0284c7', // Sky Blue
    '#d97706', // Amber / Orange
    '#7c3aed', // Purple
    '#0B2B20', // Dark Green
    '#e11d48', // Crimson
    '#059669', // Emerald
    '#4f46e5'  // Indigo
];

let govCharts = {};

function initGovernmentCharts(domainLabels, domainData, statusLabels, statusData, trendLabels, trendData) {
    const defaultFont = { family: "'Plus Jakarta Sans', sans-serif" };
    const isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const animationConfig = isReducedMotion ? false : { duration: 900, easing: 'easeOutQuart' };

    // 1. Challenges by Domain Doughnut Chart
    const domainCanvas = document.getElementById('domainChart');
    if (domainCanvas && domainLabels && domainData) {
        if (govCharts.domainChart) {
            govCharts.domainChart.destroy();
        }
        govCharts.domainChart = new Chart(domainCanvas, {
            type: 'doughnut',
            data: {
                labels: domainLabels,
                datasets: [{
                    data: domainData,
                    backgroundColor: BRAND_PALETTE.slice(0, domainLabels.length),
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: animationConfig,
                cutout: '68%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            font: { ...defaultFont, size: 11 },
                            padding: 14
                        }
                    },
                    tooltip: {
                        backgroundColor: '#0B2B20',
                        titleFont: defaultFont,
                        bodyFont: defaultFont,
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(ctx) {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const val = ctx.raw;
                                const pct = total > 0 ? Math.round((val / total) * 100) : 0;
                                return ` ${ctx.label}: ${val} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 2. Challenges Status Distribution Vertical Bar Chart
    const statusCanvas = document.getElementById('statusChart');
    if (statusCanvas && statusLabels && statusData) {
        if (govCharts.statusChart) {
            govCharts.statusChart.destroy();
        }
        govCharts.statusChart = new Chart(statusCanvas, {
            type: 'bar',
            data: {
                labels: statusLabels,
                datasets: [{
                    label: 'Challenges',
                    data: statusData,
                    backgroundColor: '#124C3A',
                    borderRadius: 6,
                    borderSkipped: false,
                    hoverBackgroundColor: '#63B99A'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: animationConfig,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0B2B20',
                        titleFont: defaultFont,
                        bodyFont: defaultFont,
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(ctx) {
                                return ` Count: ${ctx.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            font: { ...defaultFont, size: 10 },
                            maxRotation: 45,
                            minRotation: 30
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(11, 43, 32, 0.06)' },
                        ticks: { stepSize: 1, precision: 0, font: defaultFont }
                    }
                }
            }
        });
    }

    // 3. Monthly Submissions Smooth Line/Area Chart
    const trendCanvas = document.getElementById('trendChart');
    if (trendCanvas && trendLabels && trendData) {
        if (govCharts.trendChart) {
            govCharts.trendChart.destroy();
        }
        govCharts.trendChart = new Chart(trendCanvas, {
            type: 'line',
            data: {
                labels: trendLabels,
                datasets: [{
                    label: 'Challenges Reported',
                    data: trendData,
                    borderColor: '#124C3A',
                    backgroundColor: 'rgba(99, 185, 154, 0.2)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointBackgroundColor: '#63B99A',
                    pointBorderColor: '#124C3A',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: animationConfig,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0B2B20',
                        titleFont: defaultFont,
                        bodyFont: defaultFont,
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(ctx) {
                                return ` ${ctx.label}: ${ctx.raw} submissions`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { ...defaultFont, size: 11 } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(11, 43, 32, 0.06)' },
                        ticks: { stepSize: 1, precision: 0, font: defaultFont }
                    }
                }
            }
        });
    }
}

let uniCharts = {};

function initUniversityCharts(statusLabels, statusData, projectLabels, projectProgress, monthlyLabels, monthlyProposals, monthlyMilestones) {
    const defaultFont = { family: "'Plus Jakarta Sans', sans-serif" };
    const isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const animationConfig = isReducedMotion ? false : { duration: 900, easing: 'easeOutQuart' };

    // 1. Challenge Assignment Status Doughnut Chart
    const statusCanvas = document.getElementById('assignmentStatusChart');
    if (statusCanvas && statusLabels && statusData) {
        if (uniCharts.statusChart) {
            uniCharts.statusChart.destroy();
        }
        // Palette: New (Amber), Accepted (Green), Declined (Muted Red), Clarification (Mint)
        const assignmentColors = [
            '#d97706', // Amber (New / Needs action)
            '#124C3A', // Forest Green (Accepted)
            '#e11d48', // Muted Red (Declined)
            '#63B99A'  // Mint (Clarification Required)
        ];
        uniCharts.statusChart = new Chart(statusCanvas, {
            type: 'doughnut',
            data: {
                labels: statusLabels,
                datasets: [{
                    data: statusData,
                    backgroundColor: assignmentColors.slice(0, statusLabels.length),
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: animationConfig,
                cutout: '68%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            font: { ...defaultFont, size: 11 },
                            padding: 12
                        }
                    },
                    tooltip: {
                        backgroundColor: '#0B2B20',
                        titleFont: defaultFont,
                        bodyFont: defaultFont,
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(ctx) {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const val = ctx.raw;
                                const pct = total > 0 ? Math.round((val / total) * 100) : 0;
                                return ` ${ctx.label}: ${val} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 2. Active Project Progress Horizontal Bar Chart
    const progressCanvas = document.getElementById('projectProgressChart');
    if (progressCanvas && projectLabels && projectProgress) {
        if (uniCharts.progressChart) {
            uniCharts.progressChart.destroy();
        }
        uniCharts.progressChart = new Chart(progressCanvas, {
            type: 'bar',
            data: {
                labels: projectLabels,
                datasets: [{
                    label: 'Completion Progress',
                    data: projectProgress,
                    backgroundColor: '#124C3A',
                    borderRadius: 6,
                    borderSkipped: false,
                    hoverBackgroundColor: '#63B99A',
                    barThickness: 20
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                animation: animationConfig,
                layout: {
                    padding: {
                        left: 4,
                        right: 12
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0B2B20',
                        titleFont: defaultFont,
                        bodyFont: defaultFont,
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(ctx) {
                                return ` Progress: ${ctx.raw}% Completed`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(11, 43, 32, 0.06)' },
                        ticks: {
                            font: defaultFont,
                            callback: function(val) {
                                return val + '%';
                            }
                        }
                    },
                    y: {
                        grid: { display: false },
                        ticks: {
                            font: { ...defaultFont, size: 10.5, weight: '500' },
                            color: '#1e293b',
                            autoSkip: false
                        }
                    }
                }
            }
        });
    }

    // 3. Monthly Research Activity Smooth Line/Area Chart
    const activityCanvas = document.getElementById('monthlyActivityChart');
    if (activityCanvas && monthlyLabels && monthlyProposals && monthlyMilestones) {
        if (uniCharts.activityChart) {
            uniCharts.activityChart.destroy();
        }
        uniCharts.activityChart = new Chart(activityCanvas, {
            type: 'line',
            data: {
                labels: monthlyLabels,
                datasets: [
                    {
                        label: 'Proposals Submitted',
                        data: monthlyProposals,
                        borderColor: '#124C3A',
                        backgroundColor: 'rgba(18, 76, 58, 0.15)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2,
                        pointBackgroundColor: '#124C3A',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 1.5,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Milestones Completed',
                        data: monthlyMilestones,
                        borderColor: '#63B99A',
                        backgroundColor: 'rgba(99, 185, 154, 0.15)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2,
                        pointBackgroundColor: '#63B99A',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 1.5,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: animationConfig,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            font: { ...defaultFont, size: 11 },
                            padding: 12
                        }
                    },
                    tooltip: {
                        backgroundColor: '#0B2B20',
                        titleFont: defaultFont,
                        bodyFont: defaultFont,
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(ctx) {
                                return ` ${ctx.dataset.label}: ${ctx.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { ...defaultFont, size: 11 } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(11, 43, 32, 0.06)' },
                        ticks: { stepSize: 1, precision: 0, font: defaultFont }
                    }
                }
            }
        });
    }

    // Backwards compatibility if uniProgressChart canvas exists
    const legacyCanvas = document.getElementById('uniProgressChart');
    if (legacyCanvas && projectLabels && projectProgress && !progressCanvas) {
        new Chart(legacyCanvas, {
            type: 'bar',
            data: {
                labels: projectLabels,
                datasets: [{
                    label: 'Progress (%)',
                    data: projectProgress,
                    backgroundColor: '#63B99A',
                    borderRadius: 6,
                    hoverBackgroundColor: '#124C3A'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, max: 100, ticks: { callback: v => v + '%' } },
                    y: { grid: { display: false } }
                }
            }
        });
    }
}
