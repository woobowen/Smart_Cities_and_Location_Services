"""P2 figures from immutable run files. No synthetic replacement of absent results."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/"task2/figures"
PALETTE_PATH = ROOT/"templates/latex/common/p2_cloud_sorbet_colors.tex"
P = {n:"#"+c for n,c in re.findall(r"\\definecolor\{(\w+)\}\{HTML\}\{([A-F0-9]+)\}", PALETTE_PATH.read_text())}
COLORS = [P[k] for k in ("C1","C2","C3","C4","Ink")]
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10, "axes.labelsize":10,
                    "axes.titlesize":11, "axes.spines.top":False, "axes.spines.right":False,
                    "axes.edgecolor":P["Muted"], "axes.labelcolor":P["Ink"],
                    "text.color":P["Ink"], "xtick.color":P["Muted"], "ytick.color":P["Muted"],
                    "figure.facecolor":P["Paper"], "axes.facecolor":P["Paper"],
                    "pdf.fonttype":42,"svg.fonttype":"none", "savefig.facecolor":P["Paper"]})


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(fig, name, inputs, claim, selection="formal"):
    path = OUT/selection/name
    path.parent.mkdir(parents=True,exist_ok=True)
    for extension in ("pdf","svg","png"):
        fig.savefig(path.with_suffix("."+extension),dpi=300,bbox_inches="tight")
    plt.close(fig)
    meta={"figure":name,"claim_scope":claim,"input_sha256":{
          str(Path(p).relative_to(ROOT)):sha(p) for p in inputs},
          "script_sha256":sha(__file__),"palette_sha256":sha(PALETTE_PATH),
          "raster_dpi":300,"native":"Matplotlib vector PDF/SVG + reproducible source"}
    path.with_suffix(".json").write_text(json.dumps(meta,indent=2))


def load_matches(run, rows, name):
    paths=[run/p for p in rows.loc[rows.method==name,"matches"]]
    objects=[json.loads(p.read_text()) for p in paths]
    return [x for group in objects for x in group],paths


def online(run):
    run = Path(run).resolve()
    metrics=run/"metrics.csv"
    d=pd.read_csv(metrics);t=d[d.scenario=="teacher"]
    names=["TBG_g2","TBG_g5","BB_recycle_t1","BBmax_recycle_t1","BB_discard_t0.5"]
    labels=["TBG gamma=2","TBG gamma=5","Batch sum, theta=1","Batch max, theta=1","Discard, theta=0.5"]
    matches={};inputs=[metrics]
    for n in names:
        a,paths=load_matches(run,t,n);matches[n]=a;inputs+=paths
    denominator=int(t[t.method==names[0]].num_requests.sum())
    # Candidate A: denominator-aware ECDF, preserving failure mass at the plateau.
    fig,axs=plt.subplots(1,2,figsize=(10.4,3.9),gridspec_kw={"width_ratios":[2.1,1]},layout="constrained")
    for i,(n,label) in enumerate(zip(names,labels)):
        x=np.sort([a["delay"] for a in matches[n]])
        if len(x):
            axs[0].step(np.r_[0,x,25],np.r_[0,np.arange(1,len(x)+1)/denominator,len(x)/denominator],
                        where="post",color=COLORS[i],label=label,ls=["-","--","-.",":","-"][i],lw=1.7)
        axs[1].plot(i,len(x)/denominator,"o",color=COLORS[i],ms=7)
        axs[1].text(i,len(x)/denominator-.08,f"{len(x)}/{denominator}",ha="center",fontsize=8)
    axs[0].set(xlabel="Pickup delay (min)",ylabel="Fraction of all requests served by delay",ylim=(0,1.04),xlim=(0,25))
    axs[0].grid(axis="y",color=P["Rule"]);axs[0].legend(loc="center right",fontsize=8,frameon=False)
    axs[1].set(xlim=(-.5,4.5),ylim=(0,1.12),ylabel="Match rate",xticks=range(5),xticklabels=["TBG2","TBG5","Sum","Max","Drop"])
    axs[1].grid(axis="y",color=P["Rule"])
    save(fig,"online_service_ecdf",inputs,"Five paired development seeds, 20 requests each; denominator is ALL 100 requests. Unmatched requests remain unserved mass.","candidates")
    # Candidate B: full raw distribution with coverage, conditional on matched orders.
    fig,ax=plt.subplots(figsize=(10.4,3.9),layout="constrained")
    arrays=[[a["delay"] for a in matches[n]] for n in names]
    v=ax.violinplot(arrays,positions=np.arange(5),showextrema=False,widths=.7,bw_method=.3)
    for i,body in enumerate(v["bodies"]):
        body.set_facecolor(COLORS[i]);body.set_alpha(.22);body.set_edgecolor(COLORS[i])
    ax.boxplot(arrays,positions=np.arange(5),widths=.12,showfliers=False,patch_artist=False)
    rng=np.random.default_rng(384)
    for i,x in enumerate(arrays):
        ax.scatter(i+rng.uniform(-.13,.13,len(x)),x,s=5,color=COLORS[i],alpha=.5)
    ax.set(xticks=range(5),xticklabels=[l+f"\nserved {len(x)}/{denominator}" for l,x in zip(labels,arrays)],ylabel="Delay of served requests (min)")
    ax.grid(axis="y",color=P["Rule"])
    save(fig,"online_conditional_raincloud",inputs,"Same raw data; Gaussian KDE bandwidth .3, raw points and box shown. Distribution conditional on service; coverage printed.","candidates")
    # Formal set adopts A; generate it directly from same code and inputs rather than copy a bitmap.
    # Additional panels show seed-level tail trade-offs, avoiding pooled-seed pseudo-replication.
    fig,axs=plt.subplots(1,2,figsize=(10.4,3.9),layout="constrained")
    for i,(n,label) in enumerate(zip(names[:4],labels[:4])):
        q=t[t.method==n].sort_values("seed")
        axs[0].scatter(q.avg_delay,q.max_delay,color=COLORS[i],marker=["o","s","^","D"][i],s=32,label=label)
        axs[0].plot(q.avg_delay.mean(),q.max_delay.mean(),"+",color=COLORS[i],ms=13,mew=2)
    axs[0].set(xlabel="Mean delay per simulated instance (min)",ylabel="Maximum delay per instance (min)")
    axs[0].grid(color=P["Rule"]);axs[0].legend(fontsize=8,frameon=False)
    for i,(n,label) in enumerate(zip(names[:4],labels[:4])):
        x=np.sort([a["delay"] for a in matches[n]])
        axs[1].step(np.r_[0,x],np.r_[0,np.arange(1,len(x)+1)/denominator],where="post",color=COLORS[i],ls=["-","--","-.",":"][i],label=label)
    x=np.sort([a["delay"] for a in matches[names[4]]])
    axs[1].step(np.r_[0,x,25],np.r_[0,np.arange(1,len(x)+1)/denominator,len(x)/denominator],where="post",color=P["Ink"],lw=1,label=f"Discard: {len(x)/denominator:.0%} service")
    axs[1].set(xlabel="Delay (min)",ylabel="Served fraction of all requests",xlim=(0,25),ylim=(0,1.03))
    axs[1].grid(axis="y",color=P["Rule"])
    save(fig,"online_delay_and_coverage",inputs,"Left: five independent synthetic input seeds per method, cross=mean. Right: all-request service ECDF; discard has missing-service mass.")
    # Single factors in a compact method-by-scenario heatmap; each cell is actual seed mean.
    scenario_names=["teacher","supply_0.5","supply_1.5","hotspot","workers_first","requests_first"]
    row_names=["TBG_g2","TBG_g5","BB_recycle_t1","BBmax_recycle_t1"]
    z=d[d.scenario.isin(scenario_names)&d.method.isin(row_names)].pivot_table(index="method",columns="scenario",values="ratio_max",aggfunc="mean").loc[row_names,scenario_names]
    fig,ax=plt.subplots(figsize=(10.4,3.2),layout="constrained")
    cmap=LinearSegmentedColormap.from_list("p2",[P["Paper"],P["P1"],P["C1"],P["C4"]])
    im=ax.imshow(z,aspect="auto",cmap=cmap,vmin=1,vmax=max(3,float(z.max().max())))
    for (i,j),v0 in np.ndenumerate(z.to_numpy()):
        ax.text(j,i,f"{v0:.2f}",ha="center",va="center",color=P["Ink"])
    ax.set(xticks=range(len(scenario_names)),xticklabels=["Teacher","Supply 0.5","Supply 1.5","Hotspot","Workers first","Requests first"],yticks=range(4),yticklabels=["TBG2","TBG5","Batch sum1","Batch max1"])
    fig.colorbar(im,ax=ax,label="Mean max-delay ratio",shrink=.85)
    save(fig,"online_scenario_matrix",[metrics],"Five seeds per cell; ratios only when achieved cardinality equals offline maximum. Every cell is a tested setting, no interpolation.")
    # Space and waiting anatomy on the seed with the median TBG5 maximum delay.
    q=t[t.method=="TBG_g5"].sort_values("max_delay");r=q.iloc[len(q)//2];seed=int(r.seed)
    inp=run/r.input;inst=json.loads(inp.read_text())
    wp={w["id"]:w for w in inst["workers"]};rp={a["id"]:a for a in inst["requests"]}
    fig,axs=plt.subplots(2,3,figsize=(10.4,6.5),layout="constrained")
    case_inputs=[inp]
    for j,n in enumerate(["TBG_g2","TBG_g5","BB_recycle_t1"]):
        rec=t[(t.method==n)&(t.seed==seed)].iloc[0];p=run/rec.matches;case_inputs.append(p)
        a=json.loads(p.read_text());ax=axs[0,j]
        segments=[[wp[x["worker_id"]]["loc"],rp[x["request_id"]]["loc"]] for x in a]
        ax.add_collection(LineCollection(segments,colors=P["C1"],linewidths=.8,alpha=.55))
        ax.scatter(*np.array([w["loc"] for w in wp.values()]).T,s=20,marker="^",color=P["C2"],label="Worker")
        ax.scatter(*np.array([r0["loc"] for r0 in rp.values()]).T,s=14,marker="o",color=P["C4"],label="Request")
        ax.set(xlim=(-.3,10.3),ylim=(-.3,10.3),xlabel="x (km)",ylabel="y (km)",title=f"{n}; seed {seed}")
        ax.set_aspect("equal");ax.legend(fontsize=7,frameon=False,loc="lower left")
        a.sort(key=lambda x:x["delay"])
        ax=axs[1,j];xx=np.arange(len(a));wait=np.array([x["wait"] for x in a]);travel=np.array([x["pickup_distance"] for x in a])
        ax.barh(xx,wait,color=P["C3"],label="Waiting");ax.barh(xx,travel,left=wait,color=P["C1"],label="Pickup travel")
        ax.set(xlabel="Delay decomposition (min)",ylabel="Matched request, ordered by delay",xlim=(0,25),yticks=[])
        ax.legend(fontsize=7,frameon=False)
    save(fig,"online_spatial_mechanism",case_inputs,"Median seed selected by TBG5 maximum delay before chart construction. One-to-one lines are pickup edges, not roads. Speed=1 km/min; maps and delay components use same requests.")
    return {"metric_rows":len(d),"ecdf_denominator":denominator,"case_seed":seed}


def online_followup():
    threshold=ROOT/"task2/results/online/threshold_diagnosis_v1/metrics.csv"
    d=pd.read_csv(threshold)
    d=d[d.method.str.startswith("TBG")].copy()
    d["gamma"]=d.method.str.extract(r"g([\d.]+)").astype(float)
    fig,axs=plt.subplots(1,2,figsize=(10.4,3.8),layout="constrained")
    for i,scenario in enumerate(["teacher","workers_first","requests_first"]):
        q=d[d.scenario==scenario].groupby("gamma").agg(max_delay=("max_delay","mean"),sd=("max_delay","std"),fraction=("finalization_fraction","mean"))
        axs[0].errorbar(q.index,q.max_delay,yerr=q.sd,marker=["o","s","^"][i],capsize=2,color=COLORS[i],label=scenario.replace("_"," "))
        axs[1].plot(q.index,q.fraction,marker=["o","s","^"][i],color=COLORS[i])
    axs[0].set(xlabel="Threshold gamma (min)",ylabel="Mean maximum delay ± seed SD (min)")
    axs[1].set(xlabel="Threshold gamma (min)",ylabel="Mean fraction deferred to horizon",ylim=(-.01,.45))
    for ax in axs:ax.grid(axis="y",color=P["Rule"])
    axs[0].legend(fontsize=8,frameon=False)
    save(fig,"online_threshold_diagnosis",[threshold],"Three arrival patterns, five paired development seeds. Error bars are SD across input seeds, not confidence intervals. Lines join tested thresholds only.")
    proxy=ROOT/"task2/results/online/foursquare_proxy_v1/metrics.csv"
    if proxy.is_file():
        d=pd.read_csv(proxy);d["hour"]=d.scenario.str.extract(r"hour(\d+)").astype(int)
        names=["TBG_g5","TBG_g15","BB_recycle_t2","BBmax_recycle_t2"]
        fig,axs=plt.subplots(1,2,figsize=(10.4,3.7),layout="constrained")
        for i,n in enumerate(names):
            q=d[d.method==n].groupby("hour")
            x=np.array(list(q.groups));z=q[["avg_delay","max_delay"]].mean()
            for ax,col in zip(axs,["avg_delay","max_delay"]):
                ax.plot(x,z[col],color=COLORS[i],marker=["o","s","^","D"][i],label=n)
        axs[0].set(xlabel="Source local hour",ylabel="Mean pickup delay (min)")
        axs[1].set(xlabel="Source local hour",ylabel="Mean maximum delay (min)")
        for ax in axs:ax.set_xticks([8,13,18,23]);ax.grid(axis="y",color=P["Rule"])
        axs[0].legend(fontsize=8,frameon=False)
        save(fig,"online_proxy_hours",[proxy],"Historical training-inner check-in origins resampled into synthetic 60min online batches, 20 workers/requests, five paired seeds/hour; conditional local km and speed1km/min. Not observed taxi demand.")


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--online",default="task2/results/online/development_v1")
    args=p.parse_args();print(json.dumps(online(ROOT/args.online),indent=2));online_followup()
